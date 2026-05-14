from src.caro.ai.helper import *
from src.caro.config import *
# =============================================================================
# TRANSPOSITION TABLE (Bảng chuyển vị)
# Tại sao dùng? Để lưu lại điểm số của các thế cờ đã tính toán.
# Nếu trong quá trình tìm kiếm gặp lại một thế cờ đã có trong cache, Bot sẽ lấy
# kết quả ra dùng luôn, giúp tiết kiệm hàng triệu phép tính lặp lại.
# =============================================================================
TRANSPOSITION_TABLE = {}

def alpha_beta_v2(board, depth, alpha, beta, is_maximizing, radius = 1):
    # Đo đạc: Tăng số nút đã duyệt
    AI_STATS["nodes_visited"] += 1
    
    # 1. Tra cứu mã hash bàn cờ để xem đã có trong bộ nhớ đệm chưa
    board_hash = get_board_hash(board)
    
    if board_hash in TRANSPOSITION_TABLE:
        entry = TRANSPOSITION_TABLE[board_hash]
        # Chỉ dùng kết quả cũ nếu độ sâu đã tính toán lớn hơn hoặc bằng độ sâu hiện tại
        if entry['depth'] >= depth:
            # Đo đạc: Tăng số lần dùng cache
            AI_STATS["cache_hits"] += 1
            return entry['score']

    # 2. Điều kiện dừng: Nếu đã nhìn đủ xa hoặc ván đấu kết thúc
    if depth == 0 or is_terminal_node(board):
        score = evaluate_board(board)
        # Lưu vào cache trước khi trả về
        TRANSPOSITION_TABLE[board_hash] = {'depth': depth, 'score': score}
        return score

    # 3. Lấy danh sách các nước đi tiềm năng
    potential_moves = get_potential_moves(board, radius)
    
    # =========================================================================
    # TỐI ƯU: SẮP XẾP NƯỚC ĐI (Move Ordering) & GIỚI HẠN ĐỘ RỘNG (Beam Search)
    # =========================================================================
    potential_moves.sort(key=lambda m: score_move(board, m, BOT_SYMBOL if is_maximizing else HUMAN_SYMBOL), reverse=True)
    potential_moves = potential_moves[:12] 


    if is_maximizing:
        best_score = -float('inf')
        for move in potential_moves:
            make_move(board, move, BOT_SYMBOL)
            score = alpha_beta_v2(board, depth - 1, alpha, beta, False, radius)
            undo_move(board, move)
            
            best_score = max(score, best_score)
            alpha = max(alpha, best_score)
            if beta <= alpha:
                # Đo đạc: Tăng số lần cắt tỉa
                AI_STATS["pruning_count"] += 1
                break
        
        # Lưu vào cache
        TRANSPOSITION_TABLE[board_hash] = {'depth': depth, 'score': best_score}
        return best_score
    else:
        best_score = float('inf')
        for move in potential_moves:
            make_move(board, move, HUMAN_SYMBOL)
            score = alpha_beta_v2(board, depth - 1, alpha, beta, True, radius)
            undo_move(board, move)
            
            best_score = min(score, best_score)
            beta = min(beta, best_score)
            if beta <= alpha:
                # Đo đạc: Tăng số lần cắt tỉa
                AI_STATS["pruning_count"] += 1
                break
        
        # Lưu vào cache
        TRANSPOSITION_TABLE[board_hash] = {'depth': depth, 'score': best_score}
        return best_score



