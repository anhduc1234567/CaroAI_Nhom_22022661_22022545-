// scripts.js
const BOARD_SIZE = 15;
const boardElement = document.getElementById('board');
const statusElement = document.getElementById('status');
const infoElement = document.getElementById('game-info');
const startBotBtn = document.getElementById('start-bot-btn');
const historyList = document.getElementById('move-history');

const CENTER = Math.floor(BOARD_SIZE / 2);
const EMPTY_CELL = ".";
const HUMAN_SYMBOL = "X"; 
const BOT_SYMBOL = "O";   

let boardData = Array(BOARD_SIZE).fill().map(() => Array(BOARD_SIZE).fill(EMPTY_CELL));
let isBotThinking = false;
let gameActive = true;
let gameMode = 'pve'; 
let currentTurn = HUMAN_SYMBOL;
let moveCount = 0;

// 1. Khởi tạo bàn cờ và Tọa độ
function initBoard() {
    // Vẽ tọa độ ngang (1-15)
    const topCoords = document.getElementById('top-coords');
    if (topCoords) {
        topCoords.innerHTML = '';
        for(let i=1; i<=BOARD_SIZE; i++) {
            const d = document.createElement('div');
            d.className = 'coord';
            d.textContent = i;
            topCoords.appendChild(d);
        }
    }

    // Vẽ tọa độ dọc (1-15)
    const sideCoords = document.getElementById('side-coords');
    if (sideCoords) {
        sideCoords.innerHTML = '';
        for(let i=1; i<=BOARD_SIZE; i++) {
            const d = document.createElement('div');
            d.className = 'coord';
            d.textContent = i;
            sideCoords.appendChild(d);
        }
    }

    // Vẽ ô cờ
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
// Hàm lấy các giá trị hiện tại để gửi kèm vào API fetchBotMove
function getGameSettings() {
    return {
        algorithm: document.getElementById('algo-select').value,
        depth: parseInt(document.getElementById('depth-select').value),
        radius: parseInt(document.getElementById('radius-select').value)
    };
}

// 2. Cập nhật ô cờ và Lịch sử
function updateCell(r, c, symbol) {
    if (boardData[r][c] !== EMPTY_CELL && symbol !== EMPTY_CELL) return;

    boardData[r][c] = symbol;
    const cell = document.getElementById(`cell-${r}-${c}`);
    
    // Highlight nước đi mới nhất
    document.querySelectorAll('.cell.last-move').forEach(el => el.classList.remove('last-move'));

    if (cell) {
        cell.textContent = (symbol === EMPTY_CELL) ? "" : symbol;
        cell.classList.remove('x', 'o');
        if (symbol !== EMPTY_CELL) {
            cell.classList.add(symbol.toLowerCase(), 'last-move');
            addMoveToHistory(symbol, r, c);
        }
    }
}

function addMoveToHistory(symbol, r, c) {
    moveCount++;
    if (!historyList) return;
    
    const li = document.createElement('li');
    const name = (symbol === HUMAN_SYMBOL) ? "Người" : "Bot";
    const color = (symbol === HUMAN_SYMBOL) ? "var(--x-color)" : "var(--o-color)";
    
    li.innerHTML = `<b style="color: ${color}">#${moveCount}</b> - ${name} (${symbol}): [H:${r+1}, C:${c+1}]`;
    historyList.prepend(li); // Nước mới nhất lên đầu
}

// 3. Xử lý logic thắng/thua
function checkWin(r, c) {
    const symbol = boardData[r][c];
    if (symbol === EMPTY_CELL) return false;

    const directions = [[0, 1], [1, 0], [1, 1], [1, -1]];
    for (let [dr, dc] of directions) {
        let count = 1;
        for (let s of [1, -1]) {
            let nr = r + dr * s, nc = c + dc * s;
            while (nr >= 0 && nr < BOARD_SIZE && nc >= 0 && nc < BOARD_SIZE && boardData[nr][nc] === symbol) {
                count++;
                nr += dr * s;
                nc += dc * s;
            }
        }
        if (count >= 5) return true;
    }
    return false;
}

// 4. API và AI
async function fetchBotMove(symbolForBot) {
    const settings = getGameSettings();
    try {
        const response = await fetch('http://127.0.0.1:8222/bot-move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                board: boardData,
                player: symbolForBot,
                algorithm: settings.algorithm,
                depth: settings.depth,
                radius: settings.radius
            })
        });
        return await response.json();
    } catch (e) {
        console.error("Lỗi kết nối API:", e);
        return null;
    }
}

async function handleHumanMove(r, c) {
    if (!gameActive || isBotThinking || boardData[r][c] !== EMPTY_CELL || gameMode === 'eve') return;

    updateCell(r, c, HUMAN_SYMBOL);
    
    if (checkWin(r, c)) {
        infoElement.innerHTML = "🏆 <b>BẠN ĐÃ THẮNG!</b>";
        gameActive = false;
        return;
    }

    toggleInputLock(true);
    currentTurn = BOT_SYMBOL;
    updateInfoUI();

    const result = await fetchBotMove(BOT_SYMBOL);
    if (result && result.row !== undefined) {
        updateCell(result.row, result.col, BOT_SYMBOL);
        if (checkWin(result.row, result.col)) {
            infoElement.innerHTML = "🤖 <b>MÁY ĐÃ THẮNG!</b>";
            gameActive = false;
        } else {
            currentTurn = HUMAN_SYMBOL;
            updateInfoUI();
        }
    }
    toggleInputLock(false);
}

async function startBotFight() {
    if (!gameActive || gameMode !== 'eve' || isBotThinking) return;
    
    isBotThinking = true;
    startBotBtn.disabled = true;
    startBotBtn.innerText = "🤖 Đang thi đấu...";

    // Nước đi đầu tiên nếu bàn cờ trống
    const isBoardEmpty = boardData.every(row => row.every(cell => cell === EMPTY_CELL));
    if (isBoardEmpty) {
        updateCell(CENTER, CENTER, HUMAN_SYMBOL);
        currentTurn = BOT_SYMBOL;
        await new Promise(res => setTimeout(res, 500));
    }

    while (gameActive && gameMode === 'eve') {
        updateInfoUI();
        const result = await fetchBotMove(currentTurn);
        
        if (result && result.row !== undefined) {
            updateCell(result.row, result.col, currentTurn);
            
            if (checkWin(result.row, result.col)) {
                infoElement.innerHTML = `🏆 <b>BOT ${currentTurn} CHIẾN THẮNG!</b>`;
                gameActive = false;
                break;
            }
            
            currentTurn = (currentTurn === HUMAN_SYMBOL) ? BOT_SYMBOL : HUMAN_SYMBOL;
            await new Promise(res => setTimeout(res, 500));
        } else {
            break; 
        }
    }
    
    isBotThinking = false;
    startBotBtn.disabled = false;
    startBotBtn.innerText = "▶️ Bot tự đấu (Máy vs Máy)";
}

// 5. Hỗ trợ giao diện
function changeMode() {
    const radio = document.querySelector('input[name="game-mode"]:checked');
    gameMode = radio ? radio.value : 'pve';
    if (startBotBtn) {
        startBotBtn.style.display = (gameMode === 'eve') ? 'block' : 'none';
    }
    resetGame();
}

function toggleInputLock(locked) {
    isBotThinking = locked;
    boardElement.classList.toggle('disabled', locked);
    statusElement.style.display = locked ? 'block' : 'none';
}

function updateInfoUI() {
    const icon = (currentTurn === HUMAN_SYMBOL) ? "❌" : "⭕";
    const color = (currentTurn === HUMAN_SYMBOL) ? "var(--x-color)" : "var(--o-color)";
    infoElement.innerHTML = `Lượt của: <span style="color: ${color}">${icon}</span>`;
}

function resetGame() {
    boardData = Array(BOARD_SIZE).fill().map(() => Array(BOARD_SIZE).fill(EMPTY_CELL));
    gameActive = true;
    isBotThinking = false;
    currentTurn = HUMAN_SYMBOL;
    moveCount = 0;
    if (historyList) historyList.innerHTML = '';
    if (startBotBtn) startBotBtn.disabled = false;
    
    updateInfoUI();
    initBoard();
    toggleInputLock(false);
}


// Hàm xử lý thay đổi thuật toán để giới hạn Depth
function handleAlgoChange() {
    const algo = document.getElementById('algo-select').value;
    const depthSelect = document.getElementById('depth-select');
    const optDepth4 = document.getElementById('opt-depth-4');

    if (algo === 'minimax') {
        // Nếu đang chọn depth 4 mà chuyển sang minimax thì hạ xuống 3
        if (depthSelect.value === '4') {
            depthSelect.value = '3';
        }
        optDepth4.disabled = true; // Khóa option 4
        optDepth4.style.display = 'none';
    } else {
        optDepth4.disabled = false; // Mở lại option 4
        optDepth4.style.display = 'block';
    }
}
// Khởi chạy lần đầu
initBoard();