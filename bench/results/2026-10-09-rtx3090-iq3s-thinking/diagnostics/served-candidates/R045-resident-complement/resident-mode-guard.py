"""Require explicit proof of the resident-layout experiment before timing it."""
import re


def require_resident_startup(startup):
    text = startup.decode('utf-8', errors='replace')
    if re.search(r'WARNING:.*(?:resident RAM mode does not fit|their experts fit in RAM|RAM budget.*cannot be kept)', text):
        raise ValueError('Resident experiment refuses partial/file fallback')
    match = re.search(r'^strata generate: resident RAM mode: ([\d.]+) GiB of experts in RAM \(page-locked\), (\d+) in the GPU cache;.*$', text, re.M)
    if not match:
        raise ValueError('Resident experiment requires page-locked resident mode startup proof')
    if int(match.group(2)) != 8409:
        raise ValueError('Resident experiment requires the control cache count of 8409')
    return {'resident_mode_line': match.group(0), 'resident_gib_rounded': float(match.group(1)), 'gpu_expert_count': int(match.group(2))}
