import random
from decimal import Decimal
from dataclasses import dataclass
from django.utils import timezone

from apps.contracts.models import Contract, TrafficMetric
from apps.payments.models import Payment


@dataclass
class EmulatorConfig:
    clients: int
    call_rate: int
    sms_rate: int
    data_rate: Decimal
    call_price: Decimal
    sms_price: Decimal
    data_price: Decimal
    topup_threshold: Decimal
    topup_amount: Decimal
    ticks: int


class TrafficEmulator:
    def __init__(self, config: EmulatorConfig):
        self.config = config
        self.summary = {
            'total_calls': 0,
            'total_sms': 0,
            'total_data': Decimal('0'),
            'topups': 0,
            'charges': Decimal('0'),
        }

    def run(self):
        contracts = list(Contract.objects.filter(status='active').select_related('tariff'))
        if not contracts:
            return self.summary

        for _ in range(self.config.ticks):
            sample = random.sample(contracts, min(len(contracts), self.config.clients))
            tick_calls = tick_sms = tick_topups = 0
            tick_data = Decimal('0')
            tick_charges = Decimal('0')

            for contract in sample:
                calls = random.randint(0, self.config.call_rate)
                sms = random.randint(0, self.config.sms_rate)
                data_mb = Decimal(random.uniform(0, float(self.config.data_rate))).quantize(Decimal('0.01'))

                if calls:
                    tick_calls += calls
                    amount = self.config.call_price * calls
                    tick_charges += self._charge_contract(contract, amount, 'Списание за голосовой трафик')

                if sms:
                    tick_sms += sms
                    amount = self.config.sms_price * sms
                    tick_charges += self._charge_contract(contract, amount, 'Списание за SMS')

                if data_mb > 0:
                    tick_data += data_mb
                    amount = (self.config.data_price * data_mb).quantize(Decimal('0.01'))
                    tick_charges += self._charge_contract(contract, amount, 'Списание за интернет-трафик')

                if contract.balance < self.config.topup_threshold:
                    self._topup_contract(contract, self.config.topup_amount)
                    tick_topups += 1

            if any([tick_calls, tick_sms, tick_data, tick_topups]):
                TrafficMetric.objects.create(
                    calls=tick_calls,
                    sms=tick_sms,
                    data_mb=tick_data,
                    topups=tick_topups,
                    charges=tick_charges,
                    source='emulator'
                )

            self.summary['total_calls'] += tick_calls
            self.summary['total_sms'] += tick_sms
            self.summary['total_data'] += tick_data
            self.summary['topups'] += tick_topups
            self.summary['charges'] += tick_charges

        return self.summary

    def _charge_contract(self, contract, amount, description):
        amount = amount.quantize(Decimal('0.01'))
        if amount <= 0:
            return Decimal('0')
        Payment.objects.create(
            contract=contract,
            transaction_type='charge',
            amount=amount,
            status='success',
            description=description,
            payment_method='system'
        )
        try:
            contract.deduct_balance(amount, description=description)
        except Exception:
            pass
        return amount

    def _topup_contract(self, contract, amount):
        amount = Decimal(amount).quantize(Decimal('0.01'))
        Payment.objects.create(
            contract=contract,
            transaction_type='payment',
            amount=amount,
            status='success',
            description='Автопополнение (эмулятор)',
            payment_method='auto_payment'
        )
        contract.add_balance(amount, description='Автопополнение (эмулятор)')
