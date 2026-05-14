
from src.caro.ai.helper import *
from src.caro.config import *

# =============================================================================
# BỘ NHỚ ĐỆM CHO MINIMAX
# Tương tự như Alpha-Beta, Minimax cũng cần bộ nhớ đệm để tránh duyệt lại các 
# trạng thái đã biết, giúp tăng tốc độ phản hồi cho bot "Dễ".
# =============================================================================
TRANSPOSITION_TABLE_MINIMAX = {}

def minimax(board, depth, is_maximizing, radius):
    # 1. Tra cứu bộ nhớ đệm
    AI_STATS["nodes_visited"] += 1
    
    board_hash = get_board_hash(board)
    if board_hash in TRANSPOSITION_TABLE_MINIMAX:
        entry = TRANSPOSITION_TABLE_MINIMAX[board_hash]
        if entry['depth'] >= depth:
            AI_STATS["cache_hits"] += 1
            
            return entry['score']

    # 2. Điều kiện dừng
    if depth == 0 or is_terminal_node(board):
        score = evaluate_board(board)
        TRANSPOSITION_TABLE_MINIMAX[board_hash] = {'depth': depth, 'score': score}
        return score

    # 3. Lấy nước đi tiềm năng và giới hạn độ rộng (Beam Search)
    # TỐI ƯU: Minimax không có khả năng cắt tỉa nên bắt buộc phải giới hạn hẹp (10 nước)
    # để tránh việc cây tìm kiếm bùng nổ làm đứng máy.
    potential_moves = get_potential_moves(board, radius)
    potential_moves.sort(key=lambda m: score_move(board, m, BOT_SYMBOL if is_maximizing else HUMAN_SYMBOL), reverse=True)
    # potential_moves = potential_moves[:10] 


    if is_maximizing:
        best_score = -float('inf')
        for move in potential_moves:
            make_move(board, move, BOT_SYMBOL)
            score = minimax(board, depth - 1, False,radius)
            undo_move(board, move)
            best_score = max(score, best_score)
        
        TRANSPOSITION_TABLE_MINIMAX[board_hash] = {'depth': depth, 'score': best_score}
        return best_score
    else:
        best_score = float('inf')
        for move in potential_moves:
            make_move(board, move, HUMAN_SYMBOL)
            score = minimax(board, depth - 1, True, radius)
            undo_move(board, move)
            best_score = min(score, best_score)
        
        TRANSPOSITION_TABLE_MINIMAX[board_hash] = {'depth': depth, 'score': best_score}
        return best_score