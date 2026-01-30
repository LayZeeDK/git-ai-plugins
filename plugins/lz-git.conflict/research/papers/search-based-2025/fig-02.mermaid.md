```mermaid
---
config:
  flowchart:
    nodeSpacing: 30
    rankSpacing: 50
---
flowchart LR
    subgraph RQ1["RQ1"]
        A["9,998 chunks"]
    end

    subgraph RQ234["RQ2, RQ3, and RQ4"]
        B["9,998 chunks +<br/>4,509,340 random<br/>candidates"]
    end

    subgraph Branches[" "]
        direction TB
        subgraph RQ6["RQ6"]
            E["628 random chunks"]
        end
        subgraph RQ5a["RQ5"]
            C["50 random chunks"]
        end
    end

    subgraph RQ5b["RQ5"]
        D["5 random chunks<br/>(manual analysis)"]
    end

    A --> B
    B --> C --> D
    B --> E

    style Branches fill:transparent,stroke:none
```

**Figure 2.** Diagram illustrating the datasets used for each research question. The analysis progresses from 9,998 initial chunks (RQ1), includes 4,509,340 generated candidates (RQ2-RQ4), and utilizes specific random subsets for RQ5 (50 chunks for visualization, 5 for manual analysis) and RQ6 (628 chunks).
