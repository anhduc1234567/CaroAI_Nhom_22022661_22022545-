from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# Import các logic hiện có của bạn
from src.caro.config import BOARD_SIZE
from src.caro.ai.simple_bot import choose_best_move, choose_best_move_alpha_beta

app = FastAPI()

# Cấu hình CORS để Frontend (HTML/JS) có thể gọi được API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Trong thực tế nên giới hạn lại địa chỉ cụ thể
    allow_methods=["*"],
    allow_headers=["*"],
)

# Khai báo cấu trúc dữ liệu nhận từ Frontend
class GameRequest(BaseModel):
    board: List[List[str]]
    difficulty: Optional[str] = "a" # "a" cho Minimax, "b" cho Alpha-Beta

@app.get("/")
def read_root():
    return {"message": "Caro AI API is running!"}

@app.post("/bot-move")
async def get_bot_move(request: GameRequest):
    """
    Endpoint nhận trạng thái bàn cờ và trả về nước đi tốt nhất của Bot
    """
    board = request.board
    difficulty = request.difficulty

    # Chọn thuật toán dựa trên độ khó
    if difficulty == "b":
        move = choose_best_move_alpha_beta(board, depth=4) # Tăng độ sâu lên 4
    else:
        move = choose_best_move(board, depth=2) # Mặc định là Minimax

        
    print(f"Bot move ({difficulty}): {move}")
    
    if move:
        row, col = move
        return {
            "row": row, 
            "col": col,
            "status": "success"
        }
    
    return {"status": "no_moves_available"}


# Để chạy: uvicorn main:app --reload