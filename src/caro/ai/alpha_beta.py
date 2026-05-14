
from src.caro.ai.helper import *
from src.caro.config import *


def alphabeta(board, depth, alpha, beta, is_maximizing, radius):
    print('alphabeta', alpha, beta)
    # 1. Điều kiện dừng
    if depth == 0 or is_terminal_node(board):
        return evaluate_board(board)

    potential_moves = get_ordered_moves(board, radius=radius)
    
    if is_maximizing:
        best_score = -float('inf')
        for move in potential_moves:
            make_move(board, move, BOT_SYMBOL)
            score = alphabeta(board, depth - 1, alpha, beta, False, radius)
            undo_move(board, move)
            
            best_score = max(score, best_score)
            alpha = max(alpha, best_score)
            
            # Cắt tỉa: Nếu vùng điểm hiện tại đã vượt quá giới hạn của đối thủ (beta)
            if beta <= alpha:
                print('break')
                break 
        return best_score
    else:
        best_score = float('inf')
        for move in potential_moves:
            make_move(board, move, HUMAN_SYMBOL)
            score = alphabeta(board, depth - 1, alpha, beta, True, radius)
            undo_move(board, move)
            
            best_score = min(score, best_score)
            beta = min(beta, best_score)
            
            # Cắt tỉa: Nếu vùng điểm đã nhỏ hơn mức tối thiểu mà Bot chấp nhận (alpha)
            if beta <= alpha:
                print('break')
                break
        return best_score