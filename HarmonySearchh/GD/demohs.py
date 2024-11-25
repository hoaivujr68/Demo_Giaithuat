import random

# Hàm mục tiêu cần tối ưu
def objective_function(x):
    return x ** 2  # Hàm cần tối ưu (tìm giá trị x nhỏ nhất)

# Harmony Search Parameters
HMS = 5              # Kích thước Harmony Memory (HM)
HMCR = 0.9           # Harmony Memory Consideration Rate
PAR = 0.3            # Pitch Adjustment Rate
BW = 0.05            # Bandwidth cho Pitch Adjustment
max_iterations = 100 # Số lần lặp tối đa
lower_bound = -5    # Cận dưới của không gian giải pháp
upper_bound = 5     # Cận trên của không gian giải pháp

# Khởi tạo Harmony Memory (HM)
harmony_memory = [random.uniform(lower_bound, upper_bound) for _ in range(HMS)]
harmony_fitness = [objective_function(x) for x in harmony_memory]

# Harmony Search Algorithm
for iteration in range(max_iterations):
    # Tạo giải pháp mới (New Harmony)
    new_harmony = 0
    if random.random() < HMCR:  # Chọn từ Harmony Memory
        new_harmony = random.choice(harmony_memory)
        if random.random() < PAR:  # Điều chỉnh Pitch
            new_harmony += random.uniform(-BW, BW)
    else:  # Tạo ngẫu nhiên trong không gian giải pháp
        new_harmony = random.uniform(lower_bound, upper_bound)

    # Kiểm tra biên giới để đảm bảo giải pháp hợp lệ
    new_harmony = max(min(new_harmony, upper_bound), lower_bound)
    
    # Đánh giá giải pháp mới
    new_fitness = objective_function(new_harmony)
    
    # Thay thế giải pháp kém nhất nếu giải pháp mới tốt hơn
    worst_index = harmony_fitness.index(max(harmony_fitness))
    if new_fitness < harmony_fitness[worst_index]:
        harmony_memory[worst_index] = new_harmony
        harmony_fitness[worst_index] = new_fitness

# Kết quả tối ưu
best_solution = harmony_memory[harmony_fitness.index(min(harmony_fitness))]
best_fitness = min(harmony_fitness)

print(f"Tối ưu: x = {best_solution}, f(x) = {best_fitness}")
