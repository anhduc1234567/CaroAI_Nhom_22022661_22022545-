// scripts.js
const BOARD_SIZE = 15;
const EMPTY_CELL = ".";
const HUMAN_SYMBOL = "X";
const BOT_SYMBOL = "O";

const boardElement = document.getElementById('board');
const statusElement = document.getElementById('status');
const infoElement = document.getElementById('game-info');

let boardData = Array(BOARD_SIZE).fill().map(() => Array(BOARD_SIZE).fill(EMPTY_CELL));
let isBotThinking = false;

// 1. Khởi tạo bàn cờ giao diện
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

// 2. Cập nhật dữ liệu và giao diện ô cờ
function updateCell(r, c, symbol) {
    boardData[r][c] = symbol;
    const cell = document.getElementById(`cell-${r}-${c}`);
    if (cell) {
        cell.textContent = (symbol === EMPTY_CELL) ? "" : symbol;
        cell.classList.remove('x', 'o');
        if (symbol !== EMPTY_CELL) {
            cell.classList.add(symbol.toLowerCase());
        }
    }
}

// 3. Kiểm tra thắng thua ở phía Frontend
function checkWin(r, c) {
    const symbol = boardData[r][c];
    if (symbol === EMPTY_CELL) return false;

    const directions = [[0, 1], [1, 0], [1, 1], [1, -1]];
    for (let [dr, dc] of directions) {
        let count = 1;
        let nr = r + dr, nc = c + dc;
        while (nr >= 0 && nr < BOARD_SIZE && nc >= 0 && nc < BOARD_SIZE && boardData[nr][nc] === symbol) {
            count++; nr += dr; nc += dc;
        }
        nr = r - dr; nc = c - dc;
        while (nr >= 0 && nr < BOARD_SIZE && nc >= 0 && nc < BOARD_SIZE && boardData[nr][nc] === symbol) {
            count++; nr -= dr; nc -= dc;
        }
        if (count >= 5) return true;
    }
    return false;
}

// 4. Xử lý khi người chơi click
async function handleHumanMove(r, c) {
    if (isBotThinking || boardData[r][c] !== EMPTY_CELL) return;

    updateCell(r, c, HUMAN_SYMBOL);

    if (checkWin(r, c)) {
        infoElement.innerHTML = "🏆 <b>BẠN ĐÃ THẮNG!</b>";
        isBotThinking = true;
        return;
    }

    toggleInputLock(true);
    infoElement.innerHTML = "Đang chờ: 🤖";

    try {
        const difficulty = document.getElementById('difficulty').value;
        const response = await fetch('http://127.0.0.1:8222/bot-move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                board: boardData,
                difficulty: difficulty
            })
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
        infoElement.innerHTML = 'Lượt của bạn: <span style="color: var(--x-color);">❌</span>';
    } catch (e) {
        console.error("Lỗi gọi API:", e);
        toggleInputLock(false);
        alert("Không thể kết nối với Server AI. Hãy chắc chắn bạn đã chạy main.py!");
    }
}

// 5. Hàm bật/tắt trạng thái khóa bàn cờ
function toggleInputLock(locked) {
    isBotThinking = locked;
    if (locked) {
        boardElement.classList.add('disabled');
        statusElement.style.display = 'block';
    } else {
        boardElement.classList.remove('disabled');
        statusElement.style.display = 'none';
    }
}

// 6. Reset game
function resetGame() {
    boardData = Array(BOARD_SIZE).fill().map(() => Array(BOARD_SIZE).fill(EMPTY_CELL));
    isBotThinking = false;
    infoElement.innerHTML = 'Lượt của bạn: <span style="color: var(--x-color);">❌</span>';
    initBoard();
    toggleInputLock(false);
}

// Khởi tạo bàn cờ khi load trang
initBoard();