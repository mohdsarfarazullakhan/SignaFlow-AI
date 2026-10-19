from __future__ import annotations

import hashlib
import random

from app.schemas.domain import VisionRequest, VisionResponse, VisualAdvisorRequest, VisualAdvisorResponse


def analyze_demo_video(payload: VisionRequest) -> VisionResponse:
    seed_text = f"{payload.filename}:{payload.location}:{payload.screen}:{payload.duration_seconds}"
    random.seed(int(hashlib.sha256(seed_text.encode()).hexdigest()[:8], 16))
    intervals = max(5, min(12, payload.duration_seconds // 10))
    timeline = []
    passed_total = 0
    roi_total = 0
    for index in range(intervals):
        passed = random.randint(3, 11)
        in_roi = random.randint(1, max(1, passed - 1))
        timeline.append({"time": f"{index * 10}s", "passed": passed, "in_roi": in_roi})
        passed_total += passed
        roi_total += in_roi
    engagement = round(roi_total / max(1, passed_total) * 100, 1)
    return VisionResponse(people_passed=passed_total, people_inside_roi=roi_total, estimated_engagement=engagement, average_dwell_seconds=round(random.uniform(4.2, 9.6), 1), peak_interval=max(timeline, key=lambda item: int(item["in_roi"]))["time"], timeline=timeline, mode="Demo / Simulated Analytics", privacy_notice="Anonymous aggregate metrics only. No facial recognition, identity, biometric matching, or sensitive-attribute inference is performed.")


def analyze_visual(payload: VisualAdvisorRequest) -> VisualAdvisorResponse:
    scene = (payload.scene_type or payload.filename or "storefront").lower()
    if "restaurant" in scene:
        observations = ["Likely customer-facing hospitality space", "Potential indoor menu and entrance promotion zones", "Lighting and sightlines should be validated on site"]
        categories = ["Digital Signage", "High-Brightness Displays", "Display Mounts"]
        positions = ["Behind-counter menu-board zone", "Entrance-facing promotional screen", "Waiting-area content display"]
    elif "wall" in scene or "office" in scene:
        observations = ["Large interior wall may support a digital information zone", "Cable routing and wall load require site validation"]
        categories = ["Digital Signage", "Fine-Pitch LED Displays", "Mounting Accessories"]
        positions = ["Primary eye-level wall area", "Reception or waiting zone"]
    else:
        observations = ["Storefront or entrance context detected from the supplied label", "A daylight-facing display may need a high-brightness option", "Final environmental rating requires site confirmation"]
        categories = ["High-Brightness Displays", "Outdoor Digital Signage", "One-Way Vision"]
        positions = ["Inside glass facing outward", "Entrance-side freestanding position", "Window branding zone"]
    return VisualAdvisorResponse(observations=observations, recommended_categories=categories, suggested_positions=positions, confidence="Demo guidance — visual model not configured", measurement_notice="Manual measurement and a site survey are required for final dimensions, mounting, power, and environmental suitability.")
