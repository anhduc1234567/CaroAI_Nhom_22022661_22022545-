from src.caro.config import BOARD_SIZE, EMPTY_CELL
import random 
from src.caro.config import BOARD_SIZE, EMPTY_CELL, BOT_SYMBOL
from src.caro.ai.helper import *
from src.caro.ai.min_max import minimax
from src.caro.ai.alpha_beta import alphabeta
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

def choose_best_move_by_minimax(board, depth =1, radius = 1):
    best_move = None
    best_score = -float('inf')
    print('Đang mini-max')
    for move in get_ordered_moves(board, radius):
        make_move(board, move, BOT_SYMBOL)
        score = minimax(board, depth, False, radius) # Bắt đầu đệ quy
        undo_move(board, move)
        
        if score > best_score:
            best_score = score
            best_move = move
            
    return best_move # Đây là Output cuối cùng của bạn

def choose_best_move_by_alpha_beta(board, depth=4, radius = 1): # Hãy tăng depth lên ít nhất là 2 hoặc 3
    best_move = None
    best_score = -float('inf')
    alpha = -float('inf')
    beta = float('inf')
    
    moves = get_ordered_moves(board, radius= radius)
    for move in moves:
        make_move(board, move, BOT_SYMBOL)
        # Truyền alpha và beta vào đây
        score = alphabeta(board, depth - 1, alpha, beta, False, radius)
        undo_move(board, move)
        
        if score > best_score:
            best_score = score
            best_move = move
        
        # CẬP NHẬT ALPHA: Đây là chìa khóa để các nước đi sau bị cắt tỉa
        alpha = max(alpha, best_score)
            
    return best_move