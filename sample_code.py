"""
sample_code.py
================
Pre-loaded code snippets for the "Sample Code Playground" feature.

Each snippet contains an INTENTIONAL bug so students can immediately
test the AI Code Debugger without having to write or copy-paste their
own buggy code first.

Why is this a separate file?
-----------------------------
Keeping static/reference data (like these snippets) out of app.py keeps
the route handlers in app.py focused purely on request/response logic.
This is a common Flask convention: "data lives in its own module".

Structure of each snippet dict:
    id        -> unique key, used by the frontend <select> dropdown
    name      -> human-readable label shown in the dropdown
    language  -> python | java | c | javascript
    code      -> the buggy source code, as a plain string
"""

SAMPLE_SNIPPETS = [
    {
        "id": "py_factorial",
        "name": "Python: Factorial (Infinite Recursion)",
        "language": "python",
        "code": (
            "def factorial(n):\n"
            "    # Bug: missing base case -> infinite recursion / RecursionError\n"
            "    return n * factorial(n - 1)\n\n"
            "print(factorial(5))\n"
        ),
    },
    {
        "id": "py_list_avg",
        "name": "Python: List Average (Wrong Accumulator)",
        "language": "python",
        "code": (
            "def average(numbers):\n"
            "    total = 0\n"
            "    for n in numbers:\n"
            "        total = n  # Bug: should be 'total += n'\n"
            "    return total / len(numbers)\n\n"
            "print(average([10, 20, 30, 40]))\n"
        ),
    },
    {
        "id": "java_array_sum",
        "name": "Java: Array Sum (Off-by-One / ArrayIndexOutOfBounds)",
        "language": "java",
        "code": (
            "public class ArraySum {\n"
            "    public static void main(String[] args) {\n"
            "        int[] nums = {1, 2, 3, 4, 5};\n"
            "        int sum = 0;\n"
            "        // Bug: loop condition should be i < nums.length\n"
            "        for (int i = 0; i <= nums.length; i++) {\n"
            "            sum += nums[i];\n"
            "        }\n"
            "        System.out.println(\"Sum: \" + sum);\n"
            "    }\n"
            "}\n"
        ),
    },
    {
        "id": "c_swap",
        "name": "C: Swap Function (Pass-by-Value Bug)",
        "language": "c",
        "code": (
            "#include <stdio.h>\n\n"
            "// Bug: parameters are passed by value, so the swap has no\n"
            "// effect on the caller's variables.\n"
            "void swap(int a, int b) {\n"
            "    int temp = a;\n"
            "    a = b;\n"
            "    b = temp;\n"
            "}\n\n"
            "int main() {\n"
            "    int x = 5, y = 10;\n"
            "    swap(x, y);\n"
            "    printf(\"x = %d, y = %d\\n\", x, y);\n"
            "    return 0;\n"
            "}\n"
        ),
    },
    {
        "id": "js_closure_loop",
        "name": "JavaScript: Delayed Loop (var Closure Bug)",
        "language": "javascript",
        "code": (
            "// Bug: 'var' is function-scoped, so all 3 callbacks share the\n"
            "// SAME i, and all print 3 instead of 0, 1, 2.\n"
            "for (var i = 0; i < 3; i++) {\n"
            "    setTimeout(function () {\n"
            "        console.log('Value: ' + i);\n"
            "    }, 100);\n"
            "}\n"
        ),
    },
    {
        "id": "js_loose_equality",
        "name": "JavaScript: Age Check (Loose Equality Bug)",
        "language": "javascript",
        "code": (
            "function checkAge(age) {\n"
            "    // Bug: '==' performs type coercion, so the string '18'\n"
            "    // incorrectly passes this check.\n"
            "    if (age == 18) {\n"
            "        return 'Just became an adult!';\n"
            "    }\n"
            "    return 'Not 18';\n"
            "}\n\n"
            "console.log(checkAge('18'));\n"
        ),
    },
]
