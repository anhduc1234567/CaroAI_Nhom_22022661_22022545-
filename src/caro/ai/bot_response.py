from src.caro.config import BOARD_SIZE, EMPTY_CELL
import random 
from src.caro.config import BOARD_SIZE, EMPTY_CELL, BOT_SYMBOL
from src.caro.ai.helper import *
from src.caro.ai.minimax import minimax
from src.caro.ai.alpha_beta import alphabeta
from src.caro.ai.alpha_beta_v2 import alpha_beta_v2
def choose_move(board: list[list[str]]) -> tuple[int, int] | None:
    """Temporary bot: pick the first available cell."""
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == EMPTY_CELL:
                return row, col
    return None


def choose_move_random(board: list[list[str]]) -> tuple[int, int] | None:
    """Bot chọn ngẫu nhiên một ô trống bất kỳ trên bàn cờ."""
    # 1. Tìm tất cả các ô đang trống (EMPTY_CELL)
    empty_cells = [
        (row, col) 
        for row in range(BOARD_SIZE) 
        for col in range(BOARD_SIZE) 
        if board[row][col] == EMPTY_CELL
    ]
    
    # 2. Nếu còn ô trống thì chọn ngẫu nhiên, nếu không trả về None
    if empty_cells:
        return random.choice(empty_cells)
    
    return None


def choose_best_move_by_minimax(board, depth = 2, radius = 1):
    """
    Hàm chọn nước đi cho Bot "Dễ" (Minimax).
    """
    import time
    start_time = time.time()
    
    # RESET THỐNG KÊ
    AI_STATS["nodes_visited"] = 0
    AI_STATS["cache_hits"] = 0
    AI_STATS["pruning_count"] = 0

    best_move = None
    best_score = -float('inf')
    
    # Xóa cache cũ
    from src.caro.ai.minimax import TRANSPOSITION_TABLE_MINIMAX
    TRANSPOSITION_TABLE_MINIMAX.clear()

    potential_moves = get_potential_moves(board, radius)
    potential_moves.sort(key=lambda m: score_move(board, m, BOT_SYMBOL), reverse=True)
    # potential_moves = potential_moves[:10]

    for move in potential_moves:
        make_move(board, move, BOT_SYMBOL)
        score = minimax(board, depth, False,radius) 
        undo_move(board, move)
        
        if score > best_score:
            best_score = score
            best_move = move
    
    # PHÂN TÍCH KẾT QUẢ
    end_time = time.time()
    duration = end_time - start_time
    print(f"\n--- PHÂN TÍCH MINIMAX ---")
    print(f"⏱ Thời gian: {duration:.4f} giây")
    print(f"🔍 Số nút đã duyệt: {AI_STATS['nodes_visited']}")
    print(f"💾 Tận dụng Cache: {AI_STATS['cache_hits']} lần")
    print(f"--------------------------\n")
            
    return best_move

def choose_best_move_by_alpha_beta(board, depth=4, radius=1):
    import time
    start_time = time.time()
    stats = {
        "nodes": 0,
        "cutoffs": 0
    }

    best_move = None
    best_score = -float('inf')

    alpha = -float('inf')
    beta = float('inf')

    moves = get_ordered_moves(board, radius=radius)

    for move in moves:
        make_move(board, move, BOT_SYMBOL)

        score = alphabeta(
            board,
            depth - 1,
            alpha,
            beta,
            False,
            radius,
            stats
        )

        undo_move(board, move)

        if score > best_score:
            best_score = score
            best_move = move

        alpha = max(alpha, best_score)
    end_time = time.time()
    duration = end_time - start_time
    print(f"\n--- PHÂN TÍCH ALPHA-BETA ---")
    print(f"Độ sâu {depth} độ rộng {radius}")
    print(f"⏱ Thời gian: {duration:.4f} giây")
    print(f"🔍 Số nút đã duyệt: {stats['nodes']}")
    print(f"✂️ Số lần cắt tỉa: {stats['cutoffs']} lần")
    print(f"--------------------------\n")
    return best_move


def choose_best_move_by_alpha_beta_v2(board, depth = 1,  radius=1):
    """
    Hàm chọn nước đi cho Bot "Khó" (Alpha-Beta Pruning).
    """
    import time
    start_time = time.time()

    # RESET THỐNG KÊ
    AI_STATS["nodes_visited"] = 0
    AI_STATS["cache_hits"] = 0
    AI_STATS["pruning_count"] = 0

    best_move = None
    best_score = -float('inf')
    alpha = -float('inf')
    beta = float('inf')
    
    # Xóa cache cũ
    from src.caro.ai.alpha_beta_v2 import TRANSPOSITION_TABLE
    TRANSPOSITION_TABLE.clear()
    
    potential_moves = get_potential_moves(board, radius=radius)
    potential_moves.sort(key=lambda m: score_move(board, m, BOT_SYMBOL), reverse=True)
    potential_moves = potential_moves[:15]

    for move in potential_moves:
        make_move(board, move, BOT_SYMBOL)
        score = alpha_beta_v2(board, depth, alpha, beta, False)
        undo_move(board, move)
        
        if score > best_score:
            best_score = score
            best_move = move
        
        alpha = max(alpha, best_score)
    
    # PHÂN TÍCH KẾT QUẢ
    end_time = time.time()
    duration = end_time - start_time
    print(f"\n--- PHÂN TÍCH ALPHA-BETA V2 ---")
    print(f"Độ sâu {depth} độ rộng {radius}")
    print(f"⏱ Thời gian: {duration:.4f} giây")
    print(f"🔍 Số nút đã duyệt: {AI_STATS['nodes_visited']}")
    print(f"💾 Tận dụng Cache: {AI_STATS['cache_hits']} lần")
    print(f"✂️ Số lần cắt tỉa: {AI_STATS['pruning_count']} lần")
    print(f"--------------------------\n")
            
    return best_move