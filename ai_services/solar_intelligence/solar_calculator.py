# -*- coding: utf-8 -*-
"""
SolarFlow 360 — Solar Generation & Financial Savings Intelligence
================================================================
Photovoltaic yield modeling engine considering roof tilt, azimuth orientation,
shading obstruction factors, local solar insolation, and tiered DISCOM tariffs.
"""


class SolarGenerationIntelligence:
    """PV Generation, Financial Savings & Payback Estimation Engine."""

    # Orientation Yield Derate Factors (Relative to true solar south in northern hemisphere)
    ORIENTATION_FACTORS = {
        'south': 1.00,
        'southeast': 0.96,
        'southwest': 0.96,
        'east': 0.88,
        'west': 0.88,
        'northeast': 0.72,
        'northwest': 0.72,
        'north': 0.65,
    }

    # Shading Factors
    SHADING_FACTORS = {
        'no_shading': 1.00,
        'minimal': 0.94,
        'moderate': 0.80,
        'heavy': 0.58,
    }

    def __init__(self, baseline_insolation_kwh_m2_day=4.8, system_performance_ratio=0.78):
        """
        :param baseline_insolation_kwh_m2_day: Average daily solar insolation in India (kWh/m²/day)
        :param system_performance_ratio: IEC 61724 Standard PR factor (thermal losses, inverter efficiency, dust)
        """
        self.insolation = baseline_insolation_kwh_m2_day
        self.pr = system_performance_ratio

    def calculate_yield_and_roi(
        self,
        capacity_kw: float,
        roof_orientation: str = 'south',
        roof_tilt_degrees: float = 15.0,
        shading: str = 'no_shading',
        tariff_per_kwh: float = 7.5,
        system_cost: float = 185000.0,
    ) -> dict:
        """
        Compute expected solar generation, financial savings, simple payback period,
        and CO2 offset.
        """
        if capacity_kw <= 0:
            return {'status': 'error', 'message': "System capacity must be greater than 0 kW."}

        # 1. Orientation Factor
        orient_factor = self.ORIENTATION_FACTORS.get(roof_orientation.lower(), 0.90)

        # 2. Tilt Factor (Optimal tilt in India is latitude-approximate: 12° to 25°)
        if 10.0 <= roof_tilt_degrees <= 25.0:
            tilt_factor = 1.00
        elif 0.0 <= roof_tilt_degrees < 10.0:
            tilt_factor = 0.95  # Flat RCC without elevated tilted frame
        else:
            tilt_factor = 0.93  # Steep tilt

        # 3. Shading Factor
        shade_factor = self.SHADING_FACTORS.get(shading.lower(), 0.95)

        # 4. Net Effective Daily Yield (kWh / day)
        # Yield = Capacity * Peak Sun Hours * Orientation * Tilt * Shading * PR
        daily_kwh = capacity_kw * self.insolation * orient_factor * tilt_factor * shade_factor * self.pr
        monthly_kwh = daily_kwh * 30.0
        annual_kwh = daily_kwh * 365.0

        # 5. Financial Returns
        monthly_savings = monthly_kwh * tariff_per_kwh
        annual_savings = annual_kwh * tariff_per_kwh

        # 6. Simple Payback Period
        payback_years = (system_cost / annual_savings) if annual_savings > 0 else 0.0

        # 7. Environmental Impact (CEA grid emission factor ~0.82 kg CO2 / kWh in India)
        annual_co2_offset_kg = annual_kwh * 0.82

        return {
            'status': 'success',
            'system_capacity_kw': capacity_kw,
            'daily_generation_kwh': round(daily_kwh, 2),
            'monthly_generation_kwh': round(monthly_kwh, 1),
            'annual_generation_kwh': round(annual_kwh, 0),
            'monthly_savings_inr': round(monthly_savings, 0),
            'annual_savings_inr': round(annual_savings, 0),
            'estimated_payback_years': round(payback_years, 1),
            'annual_co2_offset_kg': round(annual_co2_offset_kg, 0),
            'derate_factors': {
                'orientation_factor': orient_factor,
                'tilt_factor': tilt_factor,
                'shading_factor': shade_factor,
                'system_performance_ratio_pr': self.pr,
                'peak_sun_hours_assumed': self.insolation,
            },
            'uncertainty_interval_pct': 10.0,
            'disclaimer': (
                "ESTIMATE ONLY: Generation figures represent expected statistical averages based on standard "
                "meteorological insolation data and 78% PR. Actual output varies with seasonal cloud cover, "
                "grid availability, and regular panel washing. Not an electrical output guarantee."
            ),
        }

