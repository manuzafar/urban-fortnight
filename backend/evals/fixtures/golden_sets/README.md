# Golden Sets

Golden sets are curated high-quality inception pack outputs used as baselines for regression detection.

## Creating a Golden Set

1. Generate a high-quality pack using the e2e test:
   ```bash
   cd backend
   python -m e2e_test
   ```

2. Review the output quality (score should be >= 0.8)

3. Create the golden set:
   ```bash
   python -m evals.cli create-golden \
     test_outputs/e2e_test_xxx.json \
     your_golden_set_id \
     --name "Descriptive Name"
   ```

## Listing Golden Sets

```bash
python -m evals.cli list-golden
```

## Using Golden Sets for Evaluation

```bash
python -m evals.cli run test_outputs/new_state.json \
  --golden-set banking_v1
```

## Golden Set Structure

Each golden set JSON file contains:

```json
{
  "metadata": {
    "name": "Human-readable name",
    "version": "1.0",
    "created_at": "2024-01-01T00:00:00Z",
    "quality_score": 0.85,
    "product_idea": "The product idea analyzed"
  },
  "state": {
    // Full inception pack state
    "executive_summary": {...},
    "customer_research": {...},
    "business_case": {...},
    // ... all sections
  }
}
```

## Best Practices

1. **Quality Threshold**: Only create golden sets from outputs with quality scores >= 0.8
2. **Diverse Coverage**: Include golden sets from different industries/domains
3. **Version Control**: Use semantic versioning (v1, v2) when updating golden sets
4. **Documentation**: Add clear names describing the product idea
