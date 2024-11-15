/**
 * Makes a random selection of callables (functions) from a list, executes them with their respective arguments,
 * and returns their results. The selected callables are removed from the list after being invoked.
 *
 * This function supports both synchronous and asynchronous functions. If a selected function returns a Promise,
 * it will wait for the Promise to resolve before returning the result.
 *
 * @param {CallableWithArgs[]} list - An array of callables, where each callable is represented as a tuple
 *                                    of a function and its arguments. The function will be invoked with its
 *                                    corresponding arguments.
 *                                    Each element of the array should be in the form of [Function, [args]].
 *
 * @param {number} [n=1] - The number of random selections to make. This value must not exceed the length of the list.
 *                          If not provided, the default value is 1 (i.e., one random function is chosen).
 *
 * @throws {Error} - Throws an error if the number of random selections requested exceeds the length of the list.
 *
 * @example
 * // Example 1: Synchronous functions
 * const callableList: CallableWithArgs[] = [
 *   [add, [5, 3]],           // add(5, 3)
 *   [multiply, [2, 6]]       // multiply(2, 6)
 * ];
 *
 * executeRandomCallable(callableList, 2).then(results => {
 *   console.log(results); // Output: [8, 12]
 * });
 *
 * // Example 2: Asynchronous function (greet) mixed with synchronous function (add)
 * const callableListWithAsync: CallableWithArgs[] = [
 *   [add, [5, 3]],           // add(5, 3)
 *   [greet, ['Alice']]       // greet('Alice') - async
 * ];
 *
 * executeRandomCallable(callableListWithAsync, 2).then(results => {
 *   console.log(results); // Output: ['Hello, Alice!', 8]
 * });
 *
 */
export async function executeRandomCallable(
  list: CallableWithArgs[],
  n: number = 1
): Promise<any[]> {
  if (n > list.length) {
    throw new Error("Cannot make more choices than the length of the list!");
  }

  if (n < 0) {
    throw new Error("Cannot make negative number of choices!");
  }

  const results: any[] = [];
  const availableIndexes: number[] = Array.from(
    { length: list.length },
    (_, i) => i
  );

  for (let i = 0; i < n; i++) {
    const randomIndex = Math.floor(Math.random() * availableIndexes.length);
    const selectedIndex = availableIndexes.splice(randomIndex, 1)[0]; // Remove selected callable from the available list
    const [fn, args] = list[selectedIndex];

    const result = args && args.length > 0 ? fn(...args) : fn();

    results.push(result instanceof Promise ? await result : result);
  }

  return results;
}
