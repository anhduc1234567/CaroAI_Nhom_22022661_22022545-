from src.caro.ai.helper import *
from src.caro.config import *

nodes_visited = 0

def alphabeta(board, depth, alpha, beta, is_maximizing, radius, stats):
    stats["nodes"] += 1

    # 1. Điều kiện dừng
    if depth == 0 or is_terminal_node(board):
        return evaluate_board(board)

    potential_moves = get_ordered_moves(board, radius=radius)
    
    if is_maximizing:
        best_score = -float('inf')

        for move in potential_moves:
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

            best_score = max(score, best_score)
            alpha = max(alpha, best_score)

            if beta <= alpha:
                stats["cutoffs"] += 1
                break

        return best_score

    else:
        best_score = float('inf')

        for move in potential_moves:
            make_move(board, move, HUMAN_SYMBOL)

            score = alphabeta(
                board,
                depth - 1,
                alpha,
                beta,
                True,
                radius,
                stats
            )

            undo_move(board, move)

            best_score = min(score, best_score)
            beta = min(beta, best_score)

            if beta <= alpha:
                stats["cutoffs"] += 1
                break

        return best_score