# Experimenting with Meta-predicates

<!-- toc -->

- [Specification](#specification)
- [Steps to open an editor](#steps-to-open-an-editor)
  * [If you are using Public Demo Site](#if-you-are-using-public-demo-site)
- [Experimenting with meta-annotations](#experimenting-with-meta-annotations)

<!-- tocstop -->

## Specification

For the formal language specification for the DSL
and meta-predicates 
including syntax and semantics and examples  see [](../specs/dsl.md) 

## Steps to open an editor

### If you are using Public Demo Site

1. Open https://anfisa.demo.forome.dev/
2. Select `XL_PGP3140_NIST_V42` dataset.
2. Under `Start with` section to the right of dataset names, 
   select: `Use an existing candidate set` and click `Continue`.
3. Select `PGP3140_HearingLoss_Candidates`.
4. On the right side of the page, select `Explore data or build new filter`
   and click `Open`.
5. In the top left corner, there is a listbox showing `Filter Refiner`. 
   Change it to `Decision Tree`.
6. To the right of this list box, there is another one, showing 
   `Select Decision Tree`. Click on it and select `Hearing Loss Quick`, then
   click `Apply Filter`.
7. To the right of the listbox, there is a button `Text editor`. Click
   it to show the DSL source code for the rule.
8. You can now add meta-predicates to any statement.

## Experimenting with meta-annotations

For example, if you are editing the `Hearing Loss Quick` rule,
you might want to start with the following statement:

```python
if (Clinvar_Benign in {"Benign"} and Clinvar_stars in {"2", "3", "4"}):
    return False
```

located at the line #68.

The full list of correct meta-predicates for this statement is the following:

```python
"""
@scale(variant)
@knowledge_domain("Human Genetics")
@method("Clinical Evidence")
"""
```

If you try to type something else, you will see validation errors.

For the statement at the line #57:

```python
if (Transcript_consequence not in {
        "inframe_insertion",
        "inframe_deletion",
        "missense_variant",
        "protein_altering_variant",
        "splice_region_variant",
        "synonymous_variant",
        "stop_retained_variant",
        "coding_sequence_variant"
        }):
    return False

```

The correct list of meta-annotations is:

```python
"""
@scale("Variant in Transcript")
@knowledge_domain("Functional Genetics")
@method("Bioinformatics Inference")
"""
if (Transcript_consequence not in {
        "inframe_insertion",
        "inframe_deletion",
        "missense_variant",
        "protein_altering_variant",
        "splice_region_variant",
        "synonymous_variant",
        "stop_retained_variant",
        "coding_sequence_variant"
        }):
    return False

```
Changing these values will cause validation errors.
                                           
Finally, let us take a look at the following statement at the line #75,
with the corresponding list of meta-annotations:

```python
"""
@scale(variant)
@knowledge_domain("Population Genetics")
@method(exp)
"""
if (gnomAD_AF <= .0007 and
        (gnomAD_PopMax_AN <= 2000 or gnomAD_PopMax_AF <= .01)):
    return True

```