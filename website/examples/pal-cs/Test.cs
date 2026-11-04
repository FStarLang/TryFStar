using System;
using System.Linq;
using PalCSharp.Tests;

public static class Test
{
    public static void Main()
    {
        int[][] cases = [[], [1], [3, 2, 1], [2, 2, 1, 2], [int.MaxValue, 0, int.MinValue]];
        foreach (var values in cases) Check(values);
        var random = new Random(0);
        for (int n = 0; n < 100; ++n)
            Check(Enumerable.Range(0, n).Select(_ => random.Next(-100, 100)).ToArray());
    }

    private static void Check(int[] values)
    {
        var expected = values.OrderBy(x => x).ToArray();
        SortingBySortedness.InsertionSort(values);
        if (!values.SequenceEqual(expected))
            throw new Exception("Insertion sort did not match the sorted input.");
    }
}
