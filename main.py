from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# Import các logic hiện có của bạn
from src.caro.config import BOARD_SIZE
from src.caro.ai.simple_bot import choose_best_move # Giả định đây là hàm Minimax của bạn
# Lưu ý: Bạn có thể cần điều chỉnh lại đường dẫn import tùy vào cấu trúc thư mục của bạn

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
    # Bạn có thể thêm last_move nếu thuật toán Minimax cần

@app.get("/")
def read_root():
    return {"message": "Caro AI API is running!"}

@app.post("/bot-move")
async def get_bot_move(request: GameRequest):
    """
    Endpoint nhận trạng thái bàn cờ và trả về nước đi tốt nhất của Bot
    """
    board = request.board
    # 1. Gọi hàm Minimax đã viết trước đó
    # Giả sử hàm này trả về (row, col)
    move = choose_best_move(board)
    print(move)
    if move:
        row, col = move
        return {
            "row": row, 
            "col": col,
            "status": "success"
        }
    
    return {"status": "no_moves_available"}

# Để chạy: uvicorn main:app --reload