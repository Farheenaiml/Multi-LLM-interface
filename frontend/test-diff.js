// Simple test for the diff algorithm
const { computeTextDiff } = require('./src/utils/textDiff.ts');

// Test cases
const test1 = computeTextDiff("Hello world", "Hello beautiful world");
console.log('Test 1 - Added word:', test1);

const test2 = computeTextDiff("Hello beautiful world", "Hello world");
console.log('Test 2 - Removed word:', test2);

const test3 = computeTextDiff("Hello world", "Hello world");
console.log('Test 3 - Identical:', test3);

const test4 = computeTextDiff("", "Hello world");
console.log('Test 4 - Empty to content:', test4);

const test5 = computeTextDiff("Hello world", "");
console.log('Test 5 - Content to empty:', test5);