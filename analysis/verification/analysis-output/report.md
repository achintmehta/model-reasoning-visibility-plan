# Analysis results

Analysis seed 61f43c6f3593702f, 10000 permutations, 10000 bootstrap resamples (protocol section 8.1). Holm within each family at alpha = 0.05.

## Inputs (sha256)

- un-blinding key: `6a8eeb1e310844603f4b90a5df0b429cb784954ee890482e8b06833d293f1b36`
- score sheets: `457ada360c440a4f168939fea3aeafc41f917caf474b25880dfe8381d0c59117`
- probe files: `34fc97b38384bbe1fe2551e03bd06e9831f80865445a38ce4967317c256f834a`
- quality sample: `fc739d87f523bc413ff8a1a66548f956368dd0de93d8fece3c113e1119f1d92f`
- power logs: `df43686c508aab7ab67c7ebad7d5d213e1b6845ae4de474265e3d9658cf48bcd`
- verify_smokes.py (vendored): `201744dad1dd84a2cb32df9c9bd4694841832e9c283fbeb5c1c9f6bd281c1d0d`

## Runs

60 analysed runs, 4 void attempts, 0 empty slots, 0 attempts made after their slot's analysed run (left out). 4 apps of the quality sample are void attempts and enter no analysis. 0 sampled apps have no score of record.

| model | arm | analysed_runs | void_attempts | void_rate | empty_slots | void_in_quality_sample | causes |
|---|---|---|---|---|---|---|---|
| gemma-q4 | off | 12 | 0 | 0 | 0 | 0 | none |
| gemma-q4 | seen | 12 | 0 | 0 | 0 | 0 | none |
| gemma-q4 | unseen | 12 | 2 | 0.142857 | 0 | 2 | runner failed (exit code 1): 2 |
| gptoss-20b | seen | 12 | 1 | 0.0769231 | 0 | 1 | runner failed (exit code 1): 1 |
| gptoss-20b | unseen | 12 | 1 | 0.0769231 | 0 | 1 | runner failed (exit code 1): 1 |

## Confirmatory tests (protocol sections 8.1 and 8.2)

Differences are arm b minus arm a. Steps and H4 are ratios of geometric means (b over a).

| model | family | measure | arm_a | arm_b | n_a | n_b | estimate | ci95_lo | ci95_hi | ci90_lo | ci90_hi | p | p_holm | verdict | x |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gemma-q4 | H1 | failure | unseen | seen | 12 | 12 | -0.333333 | -0.607107 | 0.0405508 | -0.574311 | -0.0169945 | 0.185381 | 0.185381 | undetermined | 0.574311 |
| gemma-q4 | H1 | steps | unseen | seen | 6 | 10 | 0.48935 | 0.32062 | 0.746876 | 0.32628 | 0.733919 | 0.0329967 | 0.0989901 | undetermined | 3.06485 |
| gemma-q4 | H1 | quality | unseen | seen | 12 | 12 | 35.1808 | 11.9143 | 58.6804 | 14.168 | 56.2201 | 0.0386961 | 0.0989901 | undetermined | 56.2201 |
| gemma-q4 | H2 | failure | off | unseen | 12 | 12 | 0.333333 | -0.0405508 | 0.607107 | 0.0169945 | 0.574311 | 0.219078 | 0.657234 | undetermined | 0.574311 |
| gemma-q4 | H2 | steps | off | unseen | 10 | 6 | 1.13052 | 0.659517 | 1.9379 | 0.684148 | 1.85492 | 0.680432 | 0.920308 | undetermined | 1.85492 |
| gemma-q4 | H2 | quality | off | unseen | 12 | 12 | -10.525 | -33.8613 | 12.2683 | -31.3022 | 9.97992 | 0.460154 | 0.920308 | undetermined | 31.3022 |
| gemma-q4 | H3-H5 | H3 | unseen | seen | 12 | 12 | 0.254255 | 0.215932 | 0.292613 | 0.22216 | 0.28728 | 9.999e-05 | 0.00029997 | supported |  |
| gemma-q4 | H3-H5 | H4 | unseen | seen | 12 | 12 | 0.362912 | 0.330099 | 0.399696 | 0.334832 | 0.39398 | 9.999e-05 | 0.00029997 | supported |  |
| gemma-q4 | H3-H5 | H5 | unseen | seen | 12 | 12 | -0.25 | -0.532305 | 0.0411067 | -0.487338 | -0.0155326 | 0.123488 | 0.123488 | not supported |  |
| gptoss-20b | H1 | failure | unseen | seen | 12 | 12 | -0.166667 | -0.448031 | 0.103762 | -0.399207 | 0.0476323 | 0.505749 | 0.505749 | undetermined | 0.399207 |
| gptoss-20b | H1 | steps | unseen | seen | 10 | 12 | 0.655654 | 0.502117 | 0.854026 | 0.522968 | 0.818443 | 0.060194 | 0.120388 | undetermined | 1.91216 |
| gptoss-20b | H1 | quality | unseen | seen | 12 | 12 | 46.5983 | 26.5168 | 66.7827 | 27.8635 | 65.336 | 0.0125987 | 0.0377962 | different |  |
| gptoss-20b | H3-H5 | H3 | unseen | seen | 12 | 12 | 0.271834 | 0.233465 | 0.309645 | 0.239077 | 0.304006 | 0.00019998 | 0.00039996 | supported |  |
| gptoss-20b | H3-H5 | H4 | unseen | seen | 12 | 12 | 0.371155 | 0.338545 | 0.405843 | 0.343361 | 0.400485 | 9.999e-05 | 0.00029997 | supported |  |
| gptoss-20b | H3-H5 | H5 | unseen | seen | 12 | 12 | -0.666667 | -0.86188 | -0.299238 | -0.840515 | -0.368076 | 0.00179982 | 0.00179982 | supported |  |

## Sensitivity (protocol section 8.3)

| analysis | model | family | measure | n_a | n_b | estimate | ci95_lo | ci95_hi | p | p_holm | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| no-nudge | gemma-q4 | H1 | failure | 10 | 10 | -0.2 | -0.521086 | 0.186962 | 0.620938 | 0.620938 | undetermined |
| no-nudge | gemma-q4 | H1 | steps | 6 | 8 | 0.49599 | 0.32149 | 0.765206 | 0.0451955 | 0.0908909 | undetermined |
| no-nudge | gemma-q4 | H1 | quality | 10 | 10 | 43.017 | 25.5345 | 60.6268 | 0.030297 | 0.0908909 | undetermined |
| substituted-0 | gemma-q4 | H1 | quality | 12 | 12 | 12.4825 | -23.0407 | 47.4972 | 0.580042 | 0.580042 | undetermined |
| substituted-0 | gemma-q4 | H2 | quality | 12 | 12 | -7.69167 | -41.2922 | 25.7427 | 0.690931 | 1 | undetermined |
| no-nudge | gptoss-20b | H1 | failure | 10 | 8 | -0.2 | -0.509838 | 0.154655 | 0.506349 | 0.771523 | undetermined |
| no-nudge | gptoss-20b | H1 | steps | 8 | 8 | 0.793104 | 0.626408 | 1.00416 | 0.385761 | 0.771523 | undetermined |
| no-nudge | gptoss-20b | H1 | quality | 10 | 8 | 39.2152 | 13.6084 | 64.7514 | 0.059994 | 0.179982 | undetermined |
| substituted-0 | gptoss-20b | H1 | quality | 12 | 12 | 38.9317 | 11.3348 | 66.8671 | 0.0368963 | 0.110689 | undetermined |

## Exploratory (protocol section 8.4, cost of section 6.2)

| analysis | model | family | measure | n_a | n_b | estimate | ci95_lo | ci95_hi |
|---|---|---|---|---|---|---|---|---|
| verification:no_verification | gemma-q4 | H1 | failure | 4 | 4 | -0.25 | -0.655287 | 0.319557 |
| verification:feedback | gemma-q4 | H1 | failure | 8 | 8 | -0.375 | -0.677696 | 0.0730408 |
| verification:difference | gemma-q4 | H1 | failure | 12 | 12 | 0.125 | -0.47915 | 0.769997 |
| verification:no_verification | gemma-q4 | H1 | steps | 2 | 3 | 0.361396 | 0.124967 | 1.04513 |
| verification:feedback | gemma-q4 | H1 | steps | 4 | 7 | 0.569384 | 0.462262 | 0.70133 |
| verification:difference | gemma-q4 | H1 | steps | 6 | 10 | 0.634713 | 0.19921 | 2.02664 |
| verification:no_verification | gemma-q4 | H1 | quality | 4 | 4 | 44.7975 | -18.8421 | 109.144 |
| verification:feedback | gemma-q4 | H1 | quality | 8 | 8 | 30.3725 | 12.4456 | 48.1421 |
| verification:difference | gemma-q4 | H1 | quality | 12 | 12 | 14.425 | -51.6378 | 80.8913 |
| quality:finished | gemma-q4 | H1 | quality | 6 | 10 | 31.5847 | -2.73358 | 66.1023 |
| api-conformance | gemma-q4 | H1 | api_conformance | 12 | 12 | 0.0833333 | -0.0935907 | 0.26011 |
| cost:all | gemma-q4 | H1 | tokens_total | 12 | 12 | 0.55786 | 0.392184 | 0.827494 |
| cost:finished | gemma-q4 | H1 | tokens_total | 6 | 10 | 0.559692 | 0.363083 | 0.960177 |
| quality:finished | gemma-q4 | H2 | quality | 10 | 6 | -9.85767 | -43.8521 | 23.6121 |
| api-conformance | gemma-q4 | H2 | api_conformance | 12 | 12 | -0.075 | -0.245884 | 0.0958841 |
| cost:all | gemma-q4 | H2 | tokens_total | 12 | 12 | 0.933584 | 0.610423 | 1.42361 |
| cost:finished | gemma-q4 | H2 | tokens_total | 10 | 6 | 1.04164 | 0.582427 | 1.73943 |
| verification:no_verification | gptoss-20b | H1 | failure | 4 | 4 | 0 | -0.489891 | 0.489891 |
| verification:feedback | gptoss-20b | H1 | failure | 8 | 8 | -0.25 | -0.590725 | 0.120284 |
| verification:difference | gptoss-20b | H1 | failure | 12 | 12 | 0.25 | -0.364087 | 0.84673 |
| verification:no_verification | gptoss-20b | H1 | steps | 4 | 4 | 0.521736 | 0.366702 | 0.742315 |
| verification:feedback | gptoss-20b | H1 | steps | 6 | 8 | 0.760182 | 0.526189 | 1.09866 |
| verification:difference | gptoss-20b | H1 | steps | 10 | 12 | 0.68633 | 0.408228 | 1.1561 |
| verification:no_verification | gptoss-20b | H1 | quality | 4 | 4 | 59.59 | 32.0906 | 87.0894 |
| verification:feedback | gptoss-20b | H1 | quality | 8 | 8 | 40.1025 | 11.5425 | 68.6625 |
| verification:difference | gptoss-20b | H1 | quality | 12 | 12 | 19.4875 | -22.4291 | 61.655 |
| quality:finished | gptoss-20b | H1 | quality | 10 | 12 | 49.6425 | 27.3098 | 71.8784 |
| api-conformance | gptoss-20b | H1 | api_conformance | 12 | 12 | -0.0208333 | -0.168147 | 0.126481 |
| cost:all | gptoss-20b | H1 | tokens_total | 12 | 12 | 0.557221 | 0.374184 | 0.812837 |
| cost:finished | gptoss-20b | H1 | tokens_total | 10 | 12 | 0.573143 | 0.396961 | 0.774304 |

## Compute and energy (protocol section 6.2)

| scope | runs | machine_h | gpu_h | energy_kwh_logged | runs_with_power_log | energy_kwh_bound_unlogged | runs_without_power_log | tokens |
|---|---|---|---|---|---|---|---|---|
| gemma-q4/off | 12 | 1.13111 | 1.19243 | 0.282778 | 12 | 0 | 0 | 5.73785e+06 |
| gemma-q4/unseen | 12 | 1.13667 | 1.27148 | 0.284167 | 12 | 0 | 0 | 5.35676e+06 |
| gemma-q4/seen | 12 | 0.602222 | 0.627081 | 0.150556 | 12 | 0 | 0 | 2.98832e+06 |
| gemma-q4/all | 36 | 2.87 | 3.09099 | 0.7175 | 36 | 0 | 0 | 1.40829e+07 |
| gptoss-20b/unseen | 12 | 0.991667 | 1.06809 | 0.247917 | 12 | 0 | 0 | 5.08245e+06 |
| gptoss-20b/seen | 12 | 0.603889 | 0.646105 | 0.150972 | 12 | 0 | 0 | 2.83204e+06 |
| gptoss-20b/all | 24 | 1.59556 | 1.71419 | 0.398889 | 24 | 0 | 0 | 7.91449e+06 |
| grid | 60 | 4.46556 | 4.80518 | 1.11639 | 60 | 0 | 0 | 2.19974e+07 |
| between runs (gaps under an hour) | 63 | 0.6825 |  |  |  |  |  |  |
| breaks between batches (gaps of an hour or more) | 0 |  |  |  |  |  |  |  |

Descriptives per model x arm (section 6.4) are in descriptives.csv, and the rubric item by item in items.csv.
