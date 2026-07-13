# Attrition — planted ground-truth drivers

Attrition_flag was generated from a logistic model. A good model trained on
`hr/employees.csv` should recover these directions and rough importances:

| Driver | Direction | Weight (logit) |
|---|---|---|
| Low engagement_score | lower -> leaves | 1.05 |
| Below-band pay (comp_ratio < 1.0) | lower -> leaves | 1.35 (x3 scaled) |
| No recent promotion (last_promotion_years > 3) | higher -> leaves | 0.28 |
| Long commute_km | higher -> leaves | 0.55 |
| Low performance_rating | lower -> leaves | 0.70 |
| Younger age | younger -> leaves | 0.50 |
| Field roles (Field Sales/Warehouse/Logistics/Production) | +0.60 bump |

Intercept -1.65; Gaussian noise sd 0.40. Overall attrition ~ generated below.
`attrition_reason` = the single strongest contributing driver per leaver.
Use this only to validate a model — never as a training feature.
