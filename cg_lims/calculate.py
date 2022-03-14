def calculate_water_volume(sample_volume: float, sample_volume_limit: float) -> float:
    """Calculates the H20 volume based on the sample volume"""
    return sample_volume_limit - sample_volume if sample_volume < sample_volume_limit else 0.0
