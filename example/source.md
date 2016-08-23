---
template: source.html
---

# slides.py example
Welcome to `slides.py`!

---

This project is just a toy of riteme.

---

Have fun!

# Basic functions
---
Markdown syntaxs provided by **Python Markdown**

---

Math formula support by Mathjax / KaTeX (which is faster, you can custom your template)

---

A simple C++ "Hello, world!" program:

```cpp
#include <iostream>

using namespace std;

int main() {
    cout << "Hello, world!" << endl;

    return 0;
}
```

# Mathjax
---
Mathjax is OK:

$$
\begin{align}
(x + y)^{n+1} & = (x + y)(x + y)^n \\
& = (x + y)\sum_{k=0}^n {n \choose k} x^ky^{n-k} \\
& = \sum_{k=0}^n {n \choose k} x^{k+1}y^{n-k} + \sum_{k=0}^n {n \choose k} x^ky^{n-k+1} \\
& = x^{n+1} + y^{n+1} + \sum_{k=0}^{n-1} {n \choose k} x^{k+1}y^{n-k} + \sum_{k=1}^n {n \choose k} x^ky^{n-k+1} \\
& = x^{n+1} + y^{n+1} + \sum_{k=1}^{n} {n \choose k - 1} x^{k}y^{n-k+1} + \sum_{k=1}^n {n \choose k} x^ky^{n-k+1} \\
& = x^{n+1} + y^{n+1} + \sum_{k=1}^n \left[{n \choose k - 1}+{n \choose k}\right] x^ky^{n-k+1} \\
& = x^{n+1} + y^{n+1} + \sum_{k=1}^n {n+1 \choose k} x^ky^{n-k+1} \\
& = \sum_{k=0}^{n+1} {n+1 \choose k} x^ky^{n-k+1} \\
\end{align}
$$

----

Also, inline math formulas: $e^{ix} = \cos x + i \sin x$

# Workflow
---
First of all, `slides.py` split your markdown source into different pages by `h1` headers and `---` seperators.

--------------------------------

Then, `slides.py` parse all the splited markdown source into html by Python Markdown.

----

Finally, print all the html pages into pdfs (using wkhtmltopdf), connect them together by pdftk.

# Thanks

That's all. Thank you. 
