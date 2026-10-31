# -*- coding: utf-8 -*-
"""
SolarFlow 360 — Intelligent Technician Optimization Engine
==========================================================
Constraint satisfaction and routing optimizer for the 15-technician field pool.
Balances skills, workload capacity, geographic proximity, and job priority.
"""

import math
from datetime import datetime, date, timedelta


class TechnicianOptimizer:
    """Intelligent Technician Dispatch & Routing Optimizer for SunPower Solutions."""

    def __init__(self, technicians=None, average_speed_kmh=35.0):
        """
        :param technicians: List of technician dicts or recordsets
        :param average_speed_kmh: City/rural road average travel speed for fallback calculation
        """
        self.technicians = technicians or []
        self.average_speed_kmh = average_speed_kmh

    def optimize_dispatch(self, unassigned_jobs: list, available_technicians: list = None) -> dict:
        """
        Optimize technician assignment across pending installation or service jobs.
        Returns explainable assignments, estimated travel times, workload metrics, and unassigned jobs.
        """
        tech_pool = available_technicians if available_technicians is not None else self.technicians
        if not tech_pool:
            return {
                'status': 'error_no_technicians',
                'assignments': [],
                'unassigned_jobs': unassigned_jobs,
                'explanations': ["No active technicians available in the workforce pool."],
                'workload_distribution': {},
            }

        # Initialize workload tracker
        workload = {t['id']: t.get('active_jobs', 0) for t in tech_pool}
        assignments = []
        unassigned = []
        explanations = []

        # Sort jobs by priority (Critical/High first) and scheduled date
        sorted_jobs = sorted(
            unassigned_jobs,
            key=lambda j: (j.get('priority', '1') == '3', j.get('priority', '1') == '2'),
            reverse=True
        )

        for job in sorted_jobs:
            candidate = self._find_best_technician(job, tech_pool, workload)
            if candidate:
                tech_id = candidate['technician']['id']
                workload[tech_id] += 1
                assignments.append({
                    'job_id': job['id'],
                    'job_name': job.get('name', 'Job'),
                    'capacity_kw': job.get('capacity_kw', 3.0),
                    'technician_id': tech_id,
                    'technician_name': candidate['technician']['name'],
                    'technician_grade': candidate['technician'].get('grade', 'junior'),
                    'estimated_travel_km': candidate['travel_km'],
                    'estimated_travel_minutes': candidate['travel_minutes'],
                    'recommended_date': job.get('scheduled_date', date.today().isoformat()),
                    'match_score': candidate['score'],
                    'reasoning': candidate['reasoning'],
                    'requires_manager_approval': True,
                })
                explanations.append(
                    f"Assigned {job.get('name', 'Job')} to {candidate['technician']['name']}: {candidate['reasoning']}"
                )
            else:
                unassigned.append({
                    'job_id': job['id'],
                    'job_name': job.get('name', 'Job'),
                    'reason': "No technician satisfied skill, certification, or daily workload capacity constraints.",
                })

        return {
            'status': 'success',
            'assignments': assignments,
            'unassigned_jobs': unassigned,
            'explanations': explanations,
            'workload_distribution': workload,
            'total_jobs_assigned': len(assignments),
            'total_jobs_unassigned': len(unassigned),
        }

    def _find_best_technician(self, job: dict, tech_pool: list, workload: dict) -> dict:
        """Score each candidate technician based on skills, capacity, and distance."""
        best_candidate = None
        best_score = -999999

        req_capacity = job.get('capacity_kw', 3.0)
        is_three_phase = req_capacity > 3.0 or job.get('system_type') == 'three_phase'
        job_lat = job.get('lat')
        job_lon = job.get('lon')

        for tech in tech_pool:
            tech_id = tech['id']
            current_load = workload[tech_id]

            # 1. Hard Constraint: Max daily workload (max 3 concurrent jobs)
            if current_load >= tech.get('max_concurrent_jobs', 3):
                continue

            # 2. Hard Constraint: Skill requirements (> 3kW requires senior/lead with electrical license)
            if is_three_phase and tech.get('grade') not in ('senior', 'lead'):
                continue

            # 3. Soft Scoring
            # Base Score
            score = 100.0

            # Workload balancing penalty (prefer technicians with fewer jobs)
            score -= (current_load * 25.0)

            # Seniority match bonus
            if tech.get('grade') == 'lead' and is_three_phase:
                score += 30.0

            # Distance calculation (Haversine formula fallback)
            travel_km = 0.0
            travel_mins = 0.0
            tech_lat = tech.get('base_lat')
            tech_lon = tech.get('base_lon')

            if job_lat and job_lon and tech_lat and tech_lon:
                travel_km = round(self._haversine_distance(tech_lat, tech_lon, job_lat, job_lon), 1)
                travel_mins = round((travel_km / self.average_speed_kmh) * 60.0)
                # Distance penalty (2 points per km)
                score -= (travel_km * 2.0)
                distance_reason = f"{travel_km} km travel (~{travel_mins} mins)"
            else:
                travel_km = 12.0  # labeled default city fallback
                travel_mins = 25.0
                distance_reason = "Default city radius (GPS coordinates unavailable)"

            reasoning = (
                f"Qualified {tech.get('grade', 'junior').title()} Technician. "
                f"Current load: {current_load} jobs. Proximity: {distance_reason}."
            )

            if score > best_score:
                best_score = score
                best_candidate = {
                    'technician': tech,
                    'score': score,
                    'travel_km': travel_km,
                    'travel_minutes': travel_mins,
                    'reasoning': reasoning,
                }

        return best_candidate

    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate great-circle distance between two GPS coordinates in kilometers."""
        R = 6371.0  # Earth radius in kilometers
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2.0) ** 2 +
            math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return R * c

