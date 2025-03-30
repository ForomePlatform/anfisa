# Anfisa Domain Specific Language

<!-- toc -->

- [Language Specification](#language-specification)
- [Variant Classification Process](#variant-classification-process)
- [Annotation classification](#annotation-classification)
- [Examples of Metapredicates](#examples-of-metapredicates)
- [How to use Statement Validation](#how-to-use-statement-validation)

<!-- tocstop -->

## Language Specification

Anfisa DSL is a specialized Python-based language designed to express rules for
classification of records. In practice, in Anfisa, a record represents a genetic
variant, and the DSL is primarily used to identify clinically relevant variants
from a whole exome or genome, thereby classifying variants into included and
excluded sets.

In Anfisa DSL, a script consists of a sequence of statements applied to a stream
of records. Each record is a shallow JSON-like structure — essentially, a
collection of key-value pairs. A key is a string from a predefined set, and its
value can be one of the primitive types: string, integer, boolean, or float. 
  
> [!IMPORTANT] For the majority of keys with string values, the values are 
> conceptually of categorical type. However, validating that 
> a string value is a valid string belonging to one of the 
> predefined categories requires defining vocabularies which
> is beyond the scope of this spec.

A record represents a genetic variant, and keys reflect the genetic 
**annotations** associated with the variant, such as provenance, biological, 
or clinical evidence.

The set of annotations, also known as keys, can be found
[here](../../app/config/dictionary/annotations.yml). 

Annotations are classified based on their purpose as follows:

* Phenotype
* Provenance
* Evidence

Evidence annotations undergo further classification according to scale,
knowledge domain, and method of acquisition. Thus, each annotation possesses
either one classification (when the purpose is `phenotype` or `provenance`) or
four classifications (`purpose`, `scale`, `knowledge_domain`, and `method`) when
it serves as evidence.

In a record, a tuple consisting of a key and value is referred to as a *
*variable**. For example:

```json
{
  "pLI":  0.9,
  "QD": 4,
  "Most_Severe_Consequence": "stop_gained",
  "Mostly_Expressed_in": "Brain - Amygdala"
}
```
                 
We say that for the record above a variable `pLI` has a float value `0.9` 
and a variable `Mostly_Expressed_in` has a string value of 
`"Brain - Amygdala"`. We also
call the variable name, e.g., `pLI` and `Mostly_Expressed_in`, or the key 
in JSON an _annotation_ because it corresponds to a genetic annotation.

The language syntax can be explained based on the following pseudo-BNF:

```
<cr> ::= '\n'
<indent> ::= (sequence of whitespace characters)

<newline> ::= <cr>
            | <newline> <cr>

<Script> ::= <Pipeline> <newline> <Action>

<Pipeline> ::= <Statement>
             | <Statement> <newline> <Pipeline>
             | <Comment> <newline> <Statement> <newline> <Pipeline>
             | <Statement> <newline> <Pipeline> <newline> <Comment>

<Comment> ::= "#" (followed by any text)

<Statement> ::= <Predicate> <cr> <indent> <Action>
              | <Validation> <newline> <Predicate> <cr> <indent> <Action>

<Action> ::= "return" <class>

<class> ::= True 
          | False

<Predicate> ::= (
        Logical expression in Python syntax that can 
        use any variables in the record with `and`, `or`, `not`, etc.
    )

<Validation> ::= '"""' <newline> <Metapredicates> <newline> '"""'

<Metapredicates> ::= <Metapredicate>
                   | <Metapredicate> <newline> <Metapredicates>

<Metapredicate> ::= '@' <classification> '(' <classification_value> ')'

<classification> ::= "purpose" 
                   | "knowledge_domain"
                   | "scale" 
                   | "method"
       

<classification_value> ::= <valid_Python_identifier>
                    | "<string surrounded by double quotes>"
```
              
> [!NOTE] For what is valid identifier, see
> [Python syntax](https://docs.python.org/3/reference/lexical_analysis.html#identifiers)
                                          
> **⚠️Warning** As per note above, conceptually any string 
> is a categorical value.
> In other words, syntactically a string is an arbitrary string
> but semantically it must belong to a set of strings defined
> in the 
> [annotations classification](../../app/config/dictionary/annotations.yml)

If a Metapredicates section is defined for a statement, then the logical
expression is validated as follows:

For each Metapredicate, there must exist a variable within the logical
expression such that its key (genetic annotation)
aligns with the classification specified by the Metapredicate.
             
## Variant Classification Process

When a script is applied to a stream of records, then the script's pipeline 
is sequentially applied to every record in a stream. As the piepline is a
sequence of statements, a record is tested with the logical expression of
each statement until either the logical expression evaluates to `True` or
a record reached the end of the pipeline (i.e., no logical expression 
evaluates to `True`). In the former case, the action in the statement is 
applied to the record, in the latter case, the last action of the script 
is applied.

Therefore, for every record we have:

1. One or zero statement(s) that evaluated to `True` for
  this record and ultimately classified it.
2. The set of statements that evaluated to `False` for this record.

When we are building a candidate set for genetic variants, a record is 
a variant and the action is either to include the variant into
candidate set or exclude it. 

## Annotation classification

Every annotation that serves as a key for variables in a record is 
classified according to 4 dimensions:

* Purpose:
  * Phenotype
  * Provenance
  * Evidence
* Knowledge Domain. Possible values are:
  * Animal Genetics
  * Call Annotations
  * Epigenetics
  * Functional Genetics
  * Human Genetics
  * Phenotypic Data
  * Population Genetics
* Scale
  * Gene 
  * Transcript
  * Window
  * Position 
  * Variant
  * Variant in a transcript
* Method
  * Bioinformatics Inference
  * Clinical Evidence
  * Experimental, Other
  * Experimental, in Vivo
  * Statistical Genetics Evidence

The full [classification](../../app/config/dictionary/annotations.yml)) 
is stored as a dictionary. 
Here are a few examples of classification for the following 4 annotations:

* Most Severe Consequence
* QD (Quality by Depth)
* pLI (gene's tolerance to loss-of-function mutations)
* Mostly Expressed in (tissues, where a gen is mostly expressed)


```yaml
Most_Severe_Consequence:
    variable_type: categorical
    name: Most_Severe_Consequence
    purpose: evidence
    Knowledge Domain:
        id: function
        name: Functional Genetics
    Scale:
        id: variant
        name: Variant
    Method:
        id: bioinf
        name: Bioinformatics Inference
    tooltip: > 
        Most Severe Consequences from the transcript with the worst annotation.\n
        The set of consequence terms is\n defined by the Sequence Ontology (SO)
        http://www.sequenceontology.org/.\n See https://m.ensembl.org/info/genome/variation/prediction/predicted_data.html\n
        for details.\n

QD:
  variable_type: numeric
  name: QD
  purpose: provenance
  Knowledge Domain:
    id: call
    name: Call Annotations
  Scale:
    id: variant
    name: Variant
  Method:
    id: na3
    name: N/A
  title: Quality by Depth
  tooltip: > 
    The QUAL score normalized by allele depth (AD) for a variant. This
    annotation puts the variant confidence QUAL score into perspective by normalizing
    for the amount of coverage available. Because each read contributes a little
    to the QUAL score, variants in regions with deep coverage can have artificially
    inflated QUAL scores, giving the impression that the call is supported by
    more evidence than it really is. To compensate for this, we normalize the
    variant confidence by depth, which gives us a more objective picture of
    how well supported the call is.

Mostly_Expressed_in:
  variable_type: categorical
  name: Mostly_Expressed_in
  purpose: evidence
  Knowledge Domain:
    id: epigenetics
    name: Epigenetics
  Scale:
    id: gene
    name: Gene
  Method:
    id: in-vivo
    name: Experimental, in Vivo

pLI:
  variable_type: numeric
  name: pLI
  purpose: evidence
  Knowledge Domain:
    id: popgen
    name: Population Genetics
  Scale:
    id: gene
    name: Gene
  Method:
    id: bioinf
    name: Bioinformatics Inference
  title: pLI Score
  tooltip: >
    The pLI score quantifies the likelihood that a gene is intolerant to mutations 
    that lead to a loss of function in the protein product. 
  variable_subtype:
    id: float
    name: float
  render-mode:
    id: linear,<
    description: Should be rendered as a linear scale. Most often, users select
      the lower bound.

```

## Examples of Metapredicates

Suppose we have a following statement:

```python
if ((0 < QD and QD < 4) or Mostly_Expressed_in not in {"brain"}):
    return False
```

This statement excludes variants of poor sequencing quality or in genes
that are not expressed in brain.

The following validation will pass for this statement:

```python
"""
@purpose(provenance)
@knowledge_domain(epigenetics)
@scale(gene)
@scale(variant)
"""
if ((0 < QD and QD < 4) or Mostly_Expressed_in not in {"brain"}):
    return False
```
            
Specifically:

* **@purpose(provenance)** is True because variable `QD` has classification
  `purpose == provenance`
* **@knowledge_domain(epigenetics)** is True because variable `Mostly_Expressed_in`
  has classification `knowledge_domain == epigenetics`
* **@scale(gene)** is True because variable `Mostly_Expressed_in`
  has classification `scale == gene`
* @scale(variant) is True because variable `QD`
  has classification `scale == variant`

On the other hand, the following validation will fail:

```python
"""
@purpose(evidence)
@knowledge_domain(human)
@scale(gene)
@scale(variant)
"""
if ((0 < QD and QD < 4) or Mostly_Expressed_in not in {"Brain - Amygdala"}):
    return False
```
        
Because no variable used in the logical expression is from knowledge 
domain `Human Genetics`

Similarly, the following validation will fail:

```python
"""
@purpose(evidence)
@scale(variant)
"""
if (pLI < 0.9):
    return False
```

Because the only variable used in the logical expression is `pLI` and
its scale is `gene`, not `variant`.

## How to use Statement Validation

The purpose of statement validation is to ensure that record classification
follows some predefined rules. For example, for variant classification a rule
might say that a variant can only be included in the candidate set based
on clinical evidence. Metapredicates allow us to validate that this rule is
indeed followed. 

For every variant included in the candidate set we can show what kind 
of evidence served as foundation for the inclusion. For every excluded
variant we can show the reason for exclusion.

