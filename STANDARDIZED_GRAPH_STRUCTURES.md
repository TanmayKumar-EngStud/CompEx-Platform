# Standardized Graph and Chart JSON Structures

## Standard Field Conventions
- Use `type` field only (remove redundant `graph` field)
- Use `x_axis` and `y_axis` (with underscores) 
- Use `label` consistently for data point identifiers
- Use lowercase with hyphens for type values: `bar-graph`, `line-graph`, `pie-chart`, `scatter-plot`
- Flat structure without nested `graph` objects

## 1. Bar-Graph Structure
```json
{
  "type": "bar-graph",
  "title": "Chart Title",
  "description": "Description of what this bar-graph shows",
  "x_axis": "X-axis Label",
  "y_axis": "Y-axis Label", 
  "data": [
    { "label": "Category A", "value": 1500 },
    { "label": "Category B", "value": 1200 },
    { "label": "Category C", "value": 900 }
  ]
}
```

## 2. Stacked Bar-Graph Structure
```json
{
  "type": "stacked-bar-graph",
  "title": "Chart Title",
  "description": "Description of what this stacked bar-graph shows",
  "x_axis": "X-axis Label",
  "y_axis": "Y-axis Label",
  "data": [
    {
      "category": "Q1",
      "values": [
        { "label": "Region A", "value": 500 },
        { "label": "Region B", "value": 300 },
        { "label": "Region C", "value": 200 }
      ]
    },
    {
      "category": "Q2", 
      "values": [
        { "label": "Region A", "value": 600 },
        { "label": "Region B", "value": 400 },
        { "label": "Region C", "value": 250 }
      ]
    }
  ]
}
```

## 3. Line-Graph Structure
```json
{
  "type": "line-graph",
  "title": "Chart Title",
  "description": "Description of what this line-graph shows",
  "x_axis": "X-axis Label",
  "y_axis": "Y-axis Label",
  "data": [
    {
      "series": "Series A",
      "values": [
        { "x": "Jan", "y": 500 },
        { "x": "Feb", "y": 700 },
        { "x": "Mar", "y": 800 }
      ]
    },
    {
      "series": "Series B",
      "values": [
        { "x": "Jan", "y": 300 },
        { "x": "Feb", "y": 450 },
        { "x": "Mar", "y": 600 }
      ]
    }
  ]
}
```

## 4. Pie-Chart Structure
```json
{
  "type": "pie-chart",
  "title": "Chart Title", 
  "description": "Description of what this pie-chart shows",
  "data": [
    { "label": "Category A", "value": 30, "color": "#FF6B6B" },
    { "label": "Category B", "value": 25, "color": "#4ECDC4" },
    { "label": "Category C", "value": 20, "color": "#45B7D1" },
    { "label": "Category D", "value": 15, "color": "#96CEB4" },
    { "label": "Category E", "value": 10, "color": "#FFEAA7" }
  ]
}
```

## 5. Scatter-Plot Structure
```json
{
  "type": "scatter-plot",
  "title": "Chart Title",
  "description": "Description of what this scatter-plot shows", 
  "x_axis": "X-axis Label",
  "y_axis": "Y-axis Label",
  "data": [
    { "label": "Point A", "x": 5000, "y": 20000 },
    { "label": "Point B", "x": 7000, "y": 30000 },
    { "label": "Point C", "x": 4000, "y": 15000 },
    { "label": "Point D", "x": 10000, "y": 40000 }
  ]
}
```

## 6. Standard Data Table Structure
```json
{
  "type": "standard-data-table",
  "title": "Table Title",
  "description": "Description of what this table shows",
  "headers": ["Column1", "Column2", "Column3", "Column4"],
  "rows": [
    ["Data1A", "Data1B", "Data1C", "Data1D"],
    ["Data2A", "Data2B", "Data2C", "Data2D"],
    ["Data3A", "Data3B", "Data3C", "Data3D"]
  ]
}
```

## 7. Pivot Table Structure
```json
{
  "type": "pivot-table",
  "title": "Table Title",
  "description": "Description of what this pivot table shows",
  "index": ["Category1", "Category2"],
  "columns": ["Metric1", "Metric2"],
  "data": {
    "Category1": { "Metric1": 10, "Metric2": 20 },
    "Category2": { "Metric1": 30, "Metric2": 40 }
  }
}
```

## 8. Time-Series Table Structure
```json
{
  "type": "time-series-table", 
  "title": "Table Title",
  "description": "Description of what this time-series table shows",
  "time_column": "Year",
  "data_columns": ["Revenue", "Expenses", "Profit"],
  "data": [
    { "Year": "2020", "Revenue": 1000000, "Expenses": 800000, "Profit": 200000 },
    { "Year": "2021", "Revenue": 1200000, "Expenses": 900000, "Profit": 300000 },
    { "Year": "2022", "Revenue": 1500000, "Expenses": 1100000, "Profit": 400000 }
  ]
}
```

## 9. Matrix Table Structure
```json
{
  "type": "matrix-table",
  "title": "Table Title", 
  "description": "Description of what this matrix table shows",
  "row_labels": ["Row1", "Row2", "Row3"],
  "column_labels": ["Col1", "Col2", "Col3"],
  "matrix": [
    [1, 0, 0],
    [0, 1, 1], 
    [1, 0, 1]
  ]
}
```

## 10. Frequency Table Structure
```json
{
  "type": "frequency-table",
  "title": "Table Title",
  "description": "Description of what this frequency table shows", 
  "categories": ["Category A", "Category B", "Category C"],
  "frequencies": [5, 10, 3]
}
```

## Common Wrapper Structure for Multiple Graphs/Tables
```json
{
  "graph/table": [
    {
      "type": "bar-graph",
      "title": "First Chart",
      // ... bar-graph structure
    },
    {
      "type": "line-graph", 
      "title": "Second Chart",
      // ... line-graph structure
    }
  ],
  "relation": "Description of how the graphs/tables relate to each other"
}
```

## Output Format for Parent-Child Questions
```json
{
  "graph/table": {
    "type": "bar-graph",
    "title": "Chart Title",
    "description": "Description of the chart",
    "x_axis": "X-axis Label",
    "y_axis": "Y-axis Label", 
    "data": [
      { "label": "Category A", "value": 100 },
      { "label": "Category B", "value": 200 }
    ]
  }
}
```

## Key Benefits of This Standardization:
1. **Consistency**: All graph types follow the same field naming conventions
2. **Simplicity**: Flat structure without unnecessary nesting
3. **Clarity**: Clear separation between chart metadata and actual data
4. **Extensibility**: Easy to add new chart types following the same pattern
5. **Parsing Efficiency**: Uniform structure simplifies data processing
6. **Maintainability**: Easier to update and modify structures across the system