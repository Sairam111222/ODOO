# -*- coding: utf-8 -*-
"""
SolarFlow 360 — AI-Assisted Roof Feasibility & Obstacle Assessment
=================================================================
Automated inspection assistant for preliminary rooftop feasibility checks.
Identifies potential obstacles, shading risks, and usable array surface ratio.
"""


import math


class RoofAssessmentAssistant:
    """Preliminary AI Roof Feasibility & Obstacle Analysis Assistant."""

    KNOWN_OBSTACLE_PATTERNS = {
        'water_tank': {'name': 'Overhead Water Storage Tank', 'setback_m': 2.5, 'shading_risk': 'high'},
        'chimney_vent': {'name': 'Plumbing Vent / Chimney Pipe', 'setback_m': 1.0, 'shading_risk': 'low'},
        'parapet_wall': {'name': 'High Perimeter Parapet Wall', 'setback_m': 1.5, 'shading_risk': 'medium'},
        'trees_foliage': {'name': 'Adjacent Tree Canopy / Foliage', 'setback_m': 3.0, 'shading_risk': 'high'},
        'ac_compressor': {'name': 'Rooftop AC Outdoor Unit', 'setback_m': 1.5, 'shading_risk': 'medium'},
        'solar_water_heater': {'name': 'Solar Water Heater / Existing Apparatus', 'setback_m': 2.0, 'shading_risk': 'medium'},
    }

    def analyze_roof_parameters(
        self,
        roof_type: str,
        total_roof_area_sqft: float,
        reported_obstacles: list = None,
        azimuth_orientation: str = 'south',
    ) -> dict:
        """
        Produce a preliminary engineering feasibility report with setback deductions,
        usable area estimation, and safety flags.
        """
        obstacles = reported_obstacles or []
        deductions_sqft = 0.0
        findings = []
        high_risk_flags = []

        # 1. Base Boundary Setback (1 meter perimeter safety corridor around edges)
        perimeter_setback_sqft = math.sqrt(max(0, total_roof_area_sqft)) * 4.0 * 2.5  # Approx safety margin
        perimeter_setback_sqft = min(perimeter_setback_sqft, total_roof_area_sqft * 0.20)
        deductions_sqft += perimeter_setback_sqft
        findings.append(f"Perimeter walkway & edge safety setback deducted: ~{perimeter_setback_sqft:.0f} sq ft.")

        # 2. Obstacle Analysis
        for obs in obstacles:
            obs_key = obs.lower().replace(' ', '_')
            spec = self.KNOWN_OBSTACLE_PATTERNS.get(obs_key, {'name': obs, 'setback_m': 1.5, 'shading_risk': 'medium'})
            obs_area_loss = spec['setback_m'] * 35.0  # Approx square feet loss per obstacle shadow
            deductions_sqft += obs_area_loss
            findings.append(f"Detected {spec['name']}: deducted {obs_area_loss:.0f} sq ft for shadow clearance.")
            if spec['shading_risk'] == 'high':
                high_risk_flags.append(f"High Shading Alert: {spec['name']} may cause string degradation in winter months.")

        usable_area_sqft = max(0.0, total_roof_area_sqft - deductions_sqft)
        usable_ratio_pct = (usable_area_sqft / total_roof_area_sqft * 100.0) if total_roof_area_sqft > 0 else 0.0

        # Maximum Capacity supported based on ~70 sq ft required per 1 kW (550W panels)
        max_possible_capacity_kw = math.floor(usable_area_sqft / 70.0)

        # Structural Safety Flags
        if roof_type in ('tin_shed', 'sloped_metal'):
            findings.append("Metal Sheet Roof: Check purlin spacing and gauge thickness before mounting.")
        elif roof_type == 'sloped_tile':
            high_risk_flags.append("Clay/Tile Roof: Tile breakage risk. Professional bracket hooks required.")

        if azimuth_orientation.lower() == 'north':
            high_risk_flags.append("North-Facing Roof: Severe generation penalty (>30%). Reverse tilt structure recommended.")

        return {
            'status': 'success',
            'total_roof_area_sqft': total_roof_area_sqft,
            'usable_solar_area_sqft': round(usable_area_sqft, 1),
            'usable_area_ratio_pct': round(usable_ratio_pct, 1),
            'max_recommended_capacity_kw': max(1.0, max_possible_capacity_kw),
            'identified_findings': findings,
            'high_risk_warnings': high_risk_flags,
            'requires_physical_survey_verification': True,
            'mandatory_disclaimer': (
                "PRELIMINARY AI ESTIMATE ONLY: Computer vision and geometric rule estimates do not replace "
                "physical structural engineering inspection. A qualified SunPower surveyor must physically "
                "inspect the roof load-bearing capacity, electrical earthing, and shade before order acceptance."
            ),
        }



