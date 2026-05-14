from src.caro.config import BOARD_SIZE, EMPTY_CELL, BOT_SYMBOL, HUMAN_SYMBOL

def get_potential_moves(board: list[list[str]], radius: int = 1) -> list[tuple[int, int]]:
    """
    Tìm các ô trống xung quanh các quân cờ đã đánh trong một phạm vi nhất định.
    Mục đích: Giảm số lượng ô cần xét cho thuật toán Minimax.
    """
    potential_moves = set() # Sử dụng set để không bị trùng lặp tọa độ

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            # Nếu ô này đã có quân (X hoặc O)
            if board[r][c] != EMPTY_CELL:
                # Quét vùng xung quanh trong phạm vi radius
                for dr in range(-radius, radius + 1):
                    for dc in range(-radius, radius + 1):
                        nr, nc = r + dr, c + dc
                        
                        # Kiểm tra xem ô (nr, nc) có nằm trong bàn cờ không
                        if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                            # Nếu là ô trống, thêm vào danh sách tiềm năng
                            if board[nr][nc] == EMPTY_CELL:
                                potential_moves.add((nr, nc))
    
    # Chuyển về list để Minimax có thể duyệt qua
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

def evaluate_board(board):
    total_score = 0
    
    # Duyệt qua tất cả các dòng, cột và đường chéo
    # Mỗi lần lấy ra một "cửa sổ" gồm 5 ô liên tiếp để chấm điểm
    
    # 1. Kiểm tra hàng ngang
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE - 4):
            window = [board[r][c+i] for i in range(5)]
            total_score += evaluate_window(window)

    # 2. Kiểm tra hàng dọc
    for c in range(BOARD_SIZE):
        for r in range(BOARD_SIZE - 4):
            window = [board[r+i][c] for i in range(5)]
            total_score += evaluate_window(window)

    # 3. Kiểm tra chéo chính (\)
    for r in range(BOARD_SIZE - 4):
        for c in range(BOARD_SIZE - 4):
            window = [board[r+i][c+i] for i in range(5)]
            total_score += evaluate_window(window)

    # 4. Kiểm tra chéo phụ (/)
    for r in range(BOARD_SIZE - 4):
        for c in range(4, BOARD_SIZE):
            window = [board[r+i][c-i] for i in range(5)]
            total_score += evaluate_window(window)

    return total_score

def evaluate_window(window):
    score = 0
    bot_count = window.count(BOT_SYMBOL)
    human_count = window.count(HUMAN_SYMBOL)
    empty_count = window.count(EMPTY_CELL)

    # --- ĐIỂM CHO BOT (Ưu tiên tấn công) ---
    if bot_count == 5:
        score += 1000000
    elif bot_count == 4 and empty_count == 1:
        score += 10000
    elif bot_count == 3 and empty_count == 2:
        score += 1000
    elif bot_count == 2 and empty_count == 3:
        score += 100

    # --- ĐIỂM CHO NGƯỜI (Phòng thủ - Chặn đối thủ) ---
    # Nếu đối thủ có 4 quân, phải trừ điểm thật nặng để Bot biết đường mà chặn
    if human_count == 4 and empty_count == 1:
        score -= 80000 # Điểm trừ lớn hơn điểm cộng của Bot để ưu tiên phòng thủ
    elif human_count == 3 and empty_count == 2:
        score -= 5000
        
    return score