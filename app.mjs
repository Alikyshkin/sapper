import { LEVELS, SapperGame } from './game.mjs';

const board = document.querySelector('#board');
const restart = document.querySelector('#restart');
const status = document.querySelector('#status');
const mines = document.querySelector('#mines');
const time = document.querySelector('#time');
const boardTip = document.querySelector('#board-tip');
const levels = document.querySelector('.levels');
const modes = document.querySelector('.modes');
const stateMessage = {
  ready: 'Выберите любую клетку',
  playing: 'Откройте все клетки без мин',
  won: 'Победа! Все безопасные клетки открыты',
  lost: 'Мина! Попробуйте ещё раз',
};

let game;
let cells = [];
let focused = 0;
let started;
let ticker;

function updateClock() {
  const seconds = started === undefined ? 0 : Math.floor((Date.now() - started) / 1000);
  time.textContent = [Math.floor(seconds / 60), seconds % 60]
    .map(part => String(part).padStart(2, '0')).join(':');
}

function selectCell(index, moveFocus = false) {
  cells[focused].tabIndex = -1;
  focused = index;
  cells[focused].tabIndex = 0;
  if (moveFocus) cells[focused].focus();
}

function render() {
  for (const [index, button] of cells.entries()) {
    const view = game.view(index);
    const row = Math.floor(index / game.size) + 1;
    const col = index % game.size + 1;
    button.dataset.kind = view.kind;
    if (view.kind === 'number') button.dataset.value = view.text;
    if (game.finished) button.setAttribute('aria-disabled', 'true');
    if (button.textContent !== view.text) button.textContent = view.text;
    button.setAttribute('aria-label', `Ряд ${row}, столбец ${col}, ${view.label}`);
  }
  board.dataset.state = game.state;
  if (status.textContent !== stateMessage[game.state]) status.textContent = stateMessage[game.state];
  const remaining = game.mines - game.marked;
  mines.textContent = remaining < 0 ? String(remaining) : String(remaining).padStart(2, '0');
}

function updateBoardTip() {
  const viewport = board.parentElement;
  boardTip.hidden = viewport.scrollWidth <= viewport.clientWidth + 1;
}

function newGame() {
  clearInterval(ticker);
  started = undefined;
  game = new SapperGame(levels.querySelector(':checked').value);
  modes.querySelector('[value="open"]').checked = true;
  focused = 0;
  board.style.setProperty('--side', game.size);
  cells = game.cells.map((_, index) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'cell';
    button.dataset.cell = index;
    button.tabIndex = index === 0 ? 0 : -1;
    return button;
  });
  board.replaceChildren(...cells);
  board.parentElement.scrollLeft = 0;
  updateClock();
  render();
  updateBoardTip();
}

function play(index, mark) {
  if (game.finished) return;
  const before = game.state;
  if (mark) game.flag(index);
  else game.reveal(index);
  if (before === 'ready' && game.state === 'playing') {
    started = Date.now();
    ticker = setInterval(updateClock, 250);
  }
  if (game.finished) {
    clearInterval(ticker);
    updateClock();
  }
  render();
}

board.addEventListener('click', event => {
  const cell = event.target.closest('.cell');
  if (!cell) return;
  const index = Number(cell.dataset.cell);
  selectCell(index);
  play(index, modes.querySelector(':checked').value === 'flag');
});

board.addEventListener('contextmenu', event => {
  const cell = event.target.closest('.cell');
  if (!cell) return;
  event.preventDefault();
  const index = Number(cell.dataset.cell);
  selectCell(index);
  play(index, true);
});

board.addEventListener('keydown', event => {
  if (!event.target.matches('.cell') || event.altKey || event.ctrlKey || event.metaKey) return;
  const index = Number(event.target.dataset.cell);
  if (event.key.toLowerCase() === 'f' || event.key.toLowerCase() === 'ф') {
    event.preventDefault();
    if (!event.repeat) play(index, true);
    return;
  }
  const x = index % game.size;
  const y = Math.floor(index / game.size);
  const moves = {
    ArrowLeft: [Math.max(0, x - 1), y],
    ArrowRight: [Math.min(game.size - 1, x + 1), y],
    ArrowUp: [x, Math.max(0, y - 1)],
    ArrowDown: [x, Math.min(game.size - 1, y + 1)],
  };
  if (!Object.hasOwn(moves, event.key)) return;
  event.preventDefault();
  const [col, row] = moves[event.key];
  selectCell(row * game.size + col, true);
});

restart.addEventListener('click', newGame);
levels.addEventListener('change', newGame);
window.addEventListener('resize', updateBoardTip);
newGame();
