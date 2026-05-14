
from src.caro.ai.helper import *
from src.caro.config import *

def minimax(board, depth, is_maximizing, radius):
    # 1. Điều kiện dừng: Nếu đã nhìn đủ xa hoặc ván đấu kết thúc
    if depth == 0 or is_terminal_node(board):
        return evaluate_board(board)
    print("Số nước potential",len(get_potential_moves(board, radius)))
    if is_maximizing:
        # Lượt của Bot: Muốn điểm số cao nhất có thể
        best_score = -float('inf')
        for move in get_potential_moves(board, radius):
            make_move(board, move, BOT_SYMBOL)
            score = minimax(board, depth - 1, False, radius) # Đệ quy xuống lượt người
            undo_move(board, move)
            best_score = max(score, best_score)
        return best_score
    else:
        # Lượt của Người: Giả định người sẽ đánh để Bot thấp điểm nhất
        best_score = float('inf')
        for move in get_potential_moves(board, radius):
            make_move(board, move, HUMAN_SYMBOL)
            score = minimax(board, depth - 1, True, radius) # Đệ quy xuống lượt Bot
            undo_move(board, move)
            best_score = min(score, best_score)
        return best_score