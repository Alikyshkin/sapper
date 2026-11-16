import assert from 'node:assert/strict';
import test from 'node:test';
import { LEVELS, SapperGame } from './game.mjs';

test('the first cell and all its neighbors are safe at every difficulty', () => {
  for (const [level, { size, mines }] of Object.entries(LEVELS)) {
    for (const first of [0, size + 1, size * size - 1]) {
      const game = new SapperGame(level, () => .19);
      game.reveal(first);
      assert.equal(game.cells[first].value, 0);
      assert.equal(game.cells[first].open, true);
      assert.equal(game.cells.filter(c => c.value === -1).length, mines);
      for (const index of game.neighbors(first)) assert.notEqual(game.cells[index].value, -1);
    }
  }
});

test('flags block opening, including the empty area expansion', () => {
  const game = new SapperGame('easy', () => .19);
  game.flag(1);
  game.reveal(1);
  assert.equal(game.state, 'ready');
  game.reveal(0);
  assert.equal(game.marked, 1);
  assert.equal(game.cells[1].open, false);
  game.flag(1);
  game.reveal(1);
  assert.equal(game.cells[1].open, true);
});

test('with the right flag, an open number reveals neighboring safe cells', () => {
  const game = new SapperGame('easy', () => .19);
  game.reveal(0);
  game.reveal(2);
  assert.equal(game.cells[3].open, false);
  game.flag(11);
  game.reveal(2);
  assert.equal(game.cells[3].open, true);
  assert.equal(game.view(11).kind, 'flag');
});

test('an incorrect adjacent flag can cause a loss', () => {
  const game = new SapperGame('easy', () => .19);
  game.reveal(0);
  game.flag(3);
  game.reveal(2);
  assert.equal(game.state, 'lost');
  assert.equal(game.view(3).kind, 'wrong');
  assert.equal(game.view(11).kind, 'exploded');
  assert.equal(game.view(4).kind, 'mine');
  game.flag(7);
  assert.equal(game.marked, 1);
});

test('all safe cells can be opened to win without marking every mine', () => {
  const game = new SapperGame('easy', () => .19);
  game.reveal(0);
  const mines = new Set([4, 11, 15, 16, 17, 18, 19, 20, 21]);
  for (const index of game.cells.keys()) {
    if (!mines.has(index)) game.reveal(index);
  }
  assert.equal(game.state, 'won');
  assert.equal(game.opened, 55);
  assert.equal(game.view(4).kind, 'mine');
  game.reveal(4);
  assert.equal(game.state, 'won');
});
