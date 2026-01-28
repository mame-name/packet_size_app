import math

def calculate_package_size(weight_per_bag, density, seal_margin=10):
    """
    weight_per_bag: 1袋あたりの充填量 (g)
    density: 比重 (g/cm3)
    seal_margin: シール幅の余白 (mm)
    """
    # 1. 必要な体積 (cm3)
    required_volume_cm3 = weight_per_bag / density
    
    # 2. 立方体に近い形状と仮定した時の理想辺長 (cm)
    # 簡易的に三方シール袋として、平置き時の面積を算出
    # 体積 V = 面積 A * 厚み t  (厚みを3cmと仮定した場合)
    assumed_thickness = 3.0 
    required_area_cm2 = required_volume_cm3 / assumed_thickness
    
    # 正方形に近い形を基準にする
    side_length_mm = math.sqrt(required_area_cm2) * 10
    
    # 3. 余白（シール幅）を考慮した外寸
    width = side_length_mm + (seal_margin * 2)
    height = (side_length_mm * 1.2) + (seal_margin * 2) # 少し縦長に補正
    
    return {
        "ideal_width": round(width, 1),
        "ideal_height": round(height, 1),
        "volume": round(required_volume_cm3, 2)
    }
