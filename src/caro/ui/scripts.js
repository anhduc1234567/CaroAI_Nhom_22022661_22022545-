// script.js
const BOARD_SIZE = 15;
const boardElement = document.getElementById('board');
const statusElement = document.getElementById('status');
const infoElement = document.getElementById('game-info');
// 1. Khởi tạo bàn cờ khi trang web load
const EMPTY_CELL = ".";
const HUMAN_SYMBOL = "X";
const BOT_SYMBOL = "O";

let boardData = Array(BOARD_SIZE).fill().map(() => Array(BOARD_SIZE).fill(EMPTY_CELL));
let isBotThinking = false;

// Cập nhật hàm khởi tạo để đồng bộ
function initBoard() {
    boardElement.innerHTML = '';
    for (let r = 0; r < BOARD_SIZE; r++) {
        for (let c = 0; c < BOARD_SIZE; c++) {
            const cell = document.createElement('div');
            cell.classList.add('cell');
            cell.id = `cell-${r}-${c}`;
            cell.addEventListener('click', () => handleHumanMove(r, c));
            boardElement.appendChild(cell);
        }
    }
}

// Cập nhật hàm updateCell để dùng đúng Symbol
function updateCell(r, c, symbol) {
    boardData[r][c] = symbol;
    const cell = document.getElementById(`cell-${r}-${c}`);
    if (cell) {
        // Nếu là EMPTY_CELL thì không hiển thị chữ
        cell.textContent = (symbol === EMPTY_CELL) ? "" : symbol;
        
        // Xóa class cũ và thêm class mới để đổi màu
        cell.classList.remove('x', 'o');
        if (symbol !== EMPTY_CELL) {
            cell.classList.add(symbol.toLowerCase());
        }
    }
}

// Cập nhật hàm checkWin để dùng EMPTY_CELL
function checkWin(r, c) {
    const symbol = boardData[r][c];
    if (symbol === EMPTY_CELL) return false;

    const directions = [[0, 1], [1, 0], [1, 1], [1, -1]];
    for (let [dr, dc] of directions) {
        let count = 1;
        // Đi tới
        let nr = r + dr, nc = c + dc;
        while (nr >= 0 && nr < BOARD_SIZE && nc >= 0 && nc < BOARD_SIZE && boardData[nr][nc] === symbol) {
            count++; nr += dr; nc += dc;
        }
        // Đi lùi
        nr = r - dr; nc = c - dc;
        while (nr >= 0 && nr < BOARD_SIZE && nc >= 0 && nc < BOARD_SIZE && boardData[nr][nc] === symbol) {
            count++; nr -= dr; nc -= dc;
        }
        if (count >= 5) return true;
    }
    return false;
}

async function handleHumanMove(r, c) {
    if (isBotThinking || boardData[r][c] !== EMPTY_CELL) return;

    // 1. Người đi
    updateCell(r, c, HUMAN_SYMBOL);
    
    if (checkWin(r, c)) {
        infoElement.innerHTML = "🏆 <b>BẠN ĐẮNG THẮNG!</b>";
        isBotThinking = true;
        return;
    }

    toggleInputLock(true);
    infoElement.innerText = "Lượt của: 🤖";

    try {
        const response = await fetch('http://127.0.0.1:8222/bot-move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ board: boardData })
        });

        const result = await response.json();

        if (result.row !== undefined) {
            updateCell(result.row, result.col, BOT_SYMBOL);

            if (checkWin(result.row, result.col)) {
                infoElement.innerHTML = "🤖 <b>MÁY ĐÃ THẮNG!</b>";
                return;
            }
        }
        
        isBotThinking = false;
        toggleInputLock(false);
        infoElement.innerText = "Lượt của: ❌";
    } catch (e) {
        console.error(e);
        toggleInputLock(false);
    }
}
// 3. Hàm giả lập Bot chọn một ô ngẫu nhiên
function simulateBotMove() {
    let emptyCells = [];
    for (let r = 0; r < BOARD_SIZE; r++) {
        for (let c = 0; c < BOARD_SIZE; c++) {
            if (boardData[r][c] === "") {
                // Bạn đang lưu là {r, c} ở đây...
                emptyCells.push({ r: r, c: c }); 
            }
        }
    }
    
    if (emptyCells.length > 0) {
        const move = emptyCells[Math.floor(Math.random() * emptyCells.length)];
        
        // ... THÌ Ở ĐÂY PHẢI GỌI LÀ move.r và move.c
        // Nếu bạn viết là move.col, nó sẽ ra undefined ngay!
        updateCell(move.r, move.c, "O"); 
    }
}

// 4. Cập nhật dữ liệu và giao diện ô cờ
function updateCell(r, c, symbol) {
    // Lưu vào mảng dữ liệu trước
    boardData[r][c] = symbol;

    // Tìm ô cờ trên giao diện
    const cellId = `cell-${r}-${c}`;
    const cell = document.getElementById(cellId);

    // KIỂM TRA: Nếu không tìm thấy ô cờ thì báo lỗi cụ thể ra console
    if (!cell) {
        console.error(`Không tìm thấy ô cờ với ID: ${cellId} tại dòng ${r}, cột ${c}`);
        return; 
    }

    // Nếu tìm thấy thì mới gán giá trị
    cell.textContent = symbol;
    cell.classList.add(symbol.toLowerCase());
}

// 5. Hàm bật/tắt trạng thái khóa
function toggleInputLock(locked) {
    isBotThinking = locked;
    if (locked) {
        boardElement.classList.add('disabled'); // CSS sẽ xử lý pointer-events: none
        statusElement.style.display = 'block';
    } else {
        boardElement.classList.remove('disabled');
        statusElement.style.display = 'none';
    }
}

// 6. Reset game
function resetGame() {
    boardData = Array(BOARD_SIZE).fill().map(() => Array(BOARD_SIZE).fill(""));
    isBotThinking = false;
    infoElement.innerText = "Lượt của: ❌";
    initBoard();
    toggleInputLock(false);
}

// Chạy khởi tạo
initBoard();