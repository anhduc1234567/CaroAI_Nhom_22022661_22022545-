from src.caro.config import BOARD_SIZE, EMPTY_CELL, BOT_SYMBOL, HUMAN_SYMBOL
import random

# =============================================================================
# ZOBRIST HASHING
# Tại sao dùng? Để biến một trạng thái bàn cờ (mảng 2D) thành một con số duy nhất.
# Giúp việc tra cứu bàn cờ trong bộ nhớ đệm (Cache) cực nhanh thay vì so sánh mảng.
# =============================================================================
ZOBRIST_TABLE = {}
for r in range(BOARD_SIZE):
    for c in range(BOARD_SIZE):
        # Mỗi ô cờ tại một vị trí (r, c) có 2 số ngẫu nhiên cho 2 loại quân (X, O)
        ZOBRIST_TABLE[(r, c, BOT_SYMBOL)] = random.getrandbits(64)
        ZOBRIST_TABLE[(r, c, HUMAN_SYMBOL)] = random.getrandbits(64)

# =============================================================================
# AI ANALYSIS & METRICS
# Bộ lưu trữ thông số đo đạc hiệu năng của AI
# =============================================================================
AI_STATS = {
    "nodes_visited": 0,  # Tổng số trạng thái đã kiểm tra
    "cache_hits": 0,     # Số lần lấy kết quả từ bộ nhớ đệm
    "pruning_count": 0,  # Số lần cắt tỉa (chỉ dành cho Alpha-Beta)
}

def get_board_hash(board):
    """
    Hàm tính mã băm (hash) cho bàn cờ hiện tại bằng phép XOR.
    Hiệu suất: Cực nhanh, giúp việc lưu trữ trạng thái vào dictionary hiệu quả.
    """
    h = 0
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            val = board[r][c]
            if val != EMPTY_CELL:
                h ^= ZOBRIST_TABLE[(r, c, val)]
    return h




def get_potential_moves(board: list[list[str]], radius: int = 2) -> list[tuple[int, int]]:
    """
    Tìm các ô trống xung quanh các quân cờ đã đánh trong một phạm vi nhất định.
    Bán kính (radius) = 2 giúp phát hiện các nước đi nhảy cách (đánh xa nhau).
    """
    potential_moves = set()

    # Tìm tất cả các vị trí đã có quân trên bàn cờ
    occupied_cells = [
        (r, c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE)
        if board[r][c] != EMPTY_CELL
    ]

    # Nếu bàn cờ chưa có quân nào, chọn ô ở chính giữa
    if not occupied_cells:
        return [(BOARD_SIZE // 2, BOARD_SIZE // 2)]

    for r, c in occupied_cells:
        # Quét vùng rộng hơn (bán kính 2) để bắt kịp các chiến thuật đánh xa
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                nr, nc = r + dr, c + dc
                if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                    if board[nr][nc] == EMPTY_CELL:
                        potential_moves.add((nr, nc))
    
    return list(potential_moves)
def quick_score(board, move):
    r, c = move
    score = 0
    # Trọng số cho các mẫu hình
    weight = {
        "consecutive_5": 100000,
        "consecutive_4": 10000,
        "consecutive_3": 1000,
        "consecutive_2": 100,
        "neighbor": 10  # Có quân bên cạnh là có điểm
    }

    for dr, dc in [(0,1), (1,0), (1,1), (1,-1)]:
        # Đếm số quân BOT và HUMAN xung quanh vị trí (r, c) theo hướng này
        bot_count = count_continuous(board, r, c, dr, dc, BOT_SYMBOL)
        human_count = count_continuous(board, r, c, dr, dc, HUMAN_SYMBOL)
        
        # Nếu đánh vào đây tạo ra chuỗi quân của mình
        if bot_count >= 4: score += weight["consecutive_5"]
        elif bot_count == 3: score += weight["consecutive_4"]
        
        # Nếu đánh vào đây để chặn đối phương
        if human_count >= 4: score += weight["consecutive_5"] # Chặn 4 cực kỳ quan trọng
        elif human_count == 3: score += weight["consecutive_4"]
        
        score += (bot_count + human_count) * weight["neighbor"]

    return score

def count_continuous(board, r, c, dr, dc, symbol):
    # Hàm phụ đếm số quân 'symbol' liên tiếp nếu đặt vào (r, c)
    count = 0
    # Kiểm tra hướng tới
    curr_r, curr_c = r + dr, c + dc
    while 0 <= curr_r < BOARD_SIZE and 0 <= curr_c < BOARD_SIZE and board[curr_r][curr_c] == symbol:
        count += 1
        curr_r += dr
        curr_c += dc
    # Kiểm tra hướng ngược lại
    curr_r, curr_c = r - dr, c - dc
    while 0 <= curr_r < BOARD_SIZE and 0 <= curr_c < BOARD_SIZE and board[curr_r][curr_c] == symbol:
        count += 1
        curr_r -= dr
        curr_c -= dc
    return count

def get_ordered_moves(board, radius=1):
    moves = set()
    scored_moves = []
    
    # 1. Tìm các ô trống xung quanh quân đã đánh
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] != EMPTY_CELL:
                for dr in range(-radius, radius + 1):
                    for dc in range(-radius, radius + 1):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr][nc] == EMPTY_CELL:
                            moves.add((nr, nc))
    
    # 2. Move Ordering (Quan trọng nhất để Alpha-Beta nhanh)
    for move in moves:
        # Chấm điểm nhanh: ô nào có nhiều quân xung quanh hơn thì ưu tiên
        score = quick_score(board, move) 
        scored_moves.append((score, move))
    
    # Sắp xếp nước tốt nhất lên đầu để Alpha-Beta cắt tỉa sớm
    scored_moves.sort(key=lambda x: x[0], reverse=True)
    return [m[1] for m in scored_moves]


def make_move(board: list[list[str]], move: tuple[int, int], symbol: str) -> None:
    """Đặt quân cờ của người chơi hoặc bot vào tọa độ chỉ định."""
    row, col = move
    board[row][col] = symbol

def undo_move(board: list[list[str]], move: tuple[int, int]) -> None:
    """Xóa quân cờ tại tọa độ chỉ định (trả về ô trống)."""
    row, col = move
    board[row][col] = EMPTY_CELL
    
def is_board_full(board):
    for row in board:
        if EMPTY_CELL in row:
            return False
    return True

def check_winner(board: list[list[str]]) -> str | None:
    """
    Kiểm tra toàn bộ bàn cờ xem có ai thắng chưa.
    Trả về: 'X' nếu Người thắng, 'O' nếu Bot thắng, None nếu chưa ai thắng.
    """
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            player = board[r][c]
            if player == EMPTY_CELL:
                continue

            # Kiểm tra 4 hướng từ ô hiện tại (r, c)
            # 1. Ngang (Sang phải)
            if c + 4 < BOARD_SIZE:
                if all(board[r][c+i] == player for i in range(5)):
                    return player

            # 2. Dọc (Xuống dưới)
            if r + 4 < BOARD_SIZE:
                if all(board[r+i][c] == player for i in range(5)):
                    return player

            # 3. Chéo chính (\ - Xuống phải)
            if r + 4 < BOARD_SIZE and c + 4 < BOARD_SIZE:
                if all(board[r+i][c+i] == player for i in range(5)):
                    return player

            # 4. Chéo phụ (/ - Xuống trái)
            if r + 4 < BOARD_SIZE and c - 4 >= 0:
                if all(board[r+i][c-i] == player for i in range(5)):
                    return player

    return None

def is_terminal_node(board):
    # 1. Kiểm tra xem có ai thắng chưa
    winner = check_winner(board) 
    if winner is not None:
        return True
        
    # 2. Kiểm tra xem bàn cờ đã đầy chưa (Hòa)
    if is_board_full(board):
        return True
        
    # Nếu chưa ai thắng và vẫn còn ô trống
    return False

def evaluate_window(window):
    score = 0
    bot_count = window.count(BOT_SYMBOL)
    human_count = window.count(HUMAN_SYMBOL)
    empty_count = window.count(EMPTY_CELL)

    # --- BOT TẤN CÔNG ---
    if bot_count == 5: return 2000000
    if bot_count == 4 and empty_count == 1: score += 50000
    if bot_count == 3 and empty_count == 2: score += 5000
    if bot_count == 2 and empty_count == 3: score += 500

    # --- CHẶN NGƯỜI CHƠI (Ưu tiên cực cao) ---
    if human_count == 4 and empty_count == 1: score -= 1000000 # Phải chặn 4 ngay
    if human_count == 3 and empty_count == 2: score -= 20000  # Chặn 3 thoáng
    if human_count == 2 and empty_count == 3: score -= 1000
        
    return score

def evaluate_board(board):
    total_score = 0
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE - 4):
            window = board[r][c:c+5]
            if any(cell != EMPTY_CELL for cell in window):
                total_score += evaluate_window(window)

    for c in range(BOARD_SIZE):
        for r in range(BOARD_SIZE - 4):
            window = [board[r+i][c] for i in range(5)]
            if any(cell != EMPTY_CELL for cell in window):
                total_score += evaluate_window(window)

    for r in range(BOARD_SIZE - 4):
        for c in range(BOARD_SIZE - 4):
            window = [board[r+i][c+i] for i in range(5)]
            if any(cell != EMPTY_CELL for cell in window):
                total_score += evaluate_window(window)

    for r in range(BOARD_SIZE - 4):
        for c in range(4, BOARD_SIZE):
            window = [board[r+i][c-i] for i in range(5)]
            if any(cell != EMPTY_CELL for cell in window):
                total_score += evaluate_window(window)
    return total_score

def score_move(board, move, symbol):
    """
    Đánh giá nước đi thông minh để sắp xếp thứ tự tìm kiếm.
    Cải tiến: Nhìn xa 4 ô để phát hiện các liên kết gián tiếp (không nằm sát nhau).
    """
    row, col = move
    opponent = HUMAN_SYMBOL if symbol == BOT_SYMBOL else BOT_SYMBOL
    
    score = 0
    directions = [(0,1), (1,0), (1,1), (1,-1)]
    
    for dr, dc in directions:
        # Tính toán cả khả năng Tấn công (symbol) và Phòng thủ (opponent)
        for s in [symbol, opponent]:
            count = 1
            # Quét xa hơn (4 ô) để tìm các quân cờ cùng loại có khả năng liên kết
            for i in range(1, 5):
                r, c = row + dr*i, col + dc*i
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == s:
                    count += 1
                else: break
            for i in range(1, 5):
                r, c = row - dr*i, col - dc*i
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == s:
                    count += 1
                else: break
            
            # Trọng số điểm cho độ dài chuỗi tiềm năng
            if count >= 5: score += 100000 if s == symbol else 80000
            elif count == 4: score += 10000 if s == symbol else 8000
            elif count == 3: score += 1000 if s == symbol else 800
            elif count == 2: score += 100
        
    # Ưu tiên các nước đi gần trung tâm để mở rộng thế trận
    center = BOARD_SIZE // 2
    score += (BOARD_SIZE - abs(row - center) - abs(col - center))
    return score
