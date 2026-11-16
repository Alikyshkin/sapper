export const LEVELS = Object.freeze({
  easy: { size: 8, mines: 9 },
  medium: { size: 12, mines: 22 },
  hard: { size: 16, mines: 40 },
});

const MINE = -1;

export class SapperGame {
  constructor(level, random = Math.random) {
    const { size, mines } = LEVELS[level];
    this.size = size;
    this.mines = mines;
    this.random = random;
    this.state = 'ready';
    this.exploded = null;
    this.marked = 0;
    this.opened = 0;
    this.cells = Array.from({ length: size * size }, () => ({
      value: 0,
      open: false,
      flag: false,
    }));
  }

  neighbors(index) {
    const x = index % this.size;
    const y = Math.floor(index / this.size);
    const result = [];
    for (let row = Math.max(0, y - 1); row <= Math.min(this.size - 1, y + 1); row++) {
      for (let col = Math.max(0, x - 1); col <= Math.min(this.size - 1, x + 1); col++) {
        const neighbor = row * this.size + col;
        if (neighbor !== index) result.push(neighbor);
      }
    }
    return result;
  }

  placeMines(first) {
    const safe = new Set([first, ...this.neighbors(first)]);
    const candidates = [...this.cells.keys()].filter(index => !safe.has(index));
    for (let i = 0; i < this.mines; i++) {
      const pick = i + Math.floor(this.random() * (candidates.length - i));
      [candidates[i], candidates[pick]] = [candidates[pick], candidates[i]];
      this.cells[candidates[i]].value = MINE;
    }
    this.cells.forEach((cell, index) => {
      if (cell.value === MINE) return;
      cell.value = this.neighbors(index).filter(neighbor => this.cells[neighbor].value === MINE).length;
    });
    this.state = 'playing';
  }

  flag(index) {
    const cell = this.cells[index];
    if (!cell || cell.open || this.finished) return;
    cell.flag = !cell.flag;
    this.marked += cell.flag ? 1 : -1;
  }

  get finished() {
    return this.state === 'won' || this.state === 'lost';
  }

  reveal(index) {
    const cell = this.cells[index];
    if (!cell || cell.flag || this.finished) return;
    if (this.state === 'ready') this.placeMines(index);

    let targets = [index];
    if (cell.open) {
      if (cell.value === 0) return;
      const neighbors = this.neighbors(index);
      if (neighbors.filter(i => this.cells[i].flag).length !== cell.value) return;
      targets = neighbors.filter(i => !this.cells[i].flag && !this.cells[i].open);
    }

    for (const target of targets) {
      if (this.cells[target].value === MINE) {
        this.exploded = target;
        this.state = 'lost';
        return;
      }
      this.openArea(target);
    }
    if (this.opened === this.cells.length - this.mines) this.state = 'won';
  }

  openArea(index) {
    const remaining = [index];
    while (remaining.length) {
      const next = remaining.pop();
      const cell = this.cells[next];
      if (cell.open || cell.flag) continue;
      cell.open = true;
      this.opened++;
      if (cell.value === 0) remaining.push(...this.neighbors(next));
    }
  }

  view(index) {
    const cell = this.cells[index];
    const mine = cell.value === MINE;
    if (this.exploded === index) return { kind: 'exploded', text: '✹', label: 'взрыв' };
    if (cell.flag) {
      if (this.finished && !mine) return { kind: 'wrong', text: '×', label: 'ошибочный флаг' };
      return { kind: 'flag', text: '⚑', label: 'флаг' };
    }
    if (this.finished && mine) return { kind: 'mine', text: '✹', label: 'мина' };
    if (!cell.open) return { kind: 'closed', text: '', label: 'закрыта' };
    if (cell.value === 0) return { kind: 'empty', text: '', label: 'открыта, мин рядом нет' };
    return { kind: 'number', text: String(cell.value), label: 'мин рядом ' + cell.value };
  }
}
