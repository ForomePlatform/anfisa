# Anfisa Domain Specific Language

## Language Specification

Anfisa DSL is a specialized Python-based language designed to express rules for classification of records.
In practice, in Anfisa, a record represents a genetic variant, and the DSL is primarily used to identify clinically relevant variants from a whole exome or genome, thereby classifying variants into included and excluded sets.

In Anfisa DSL, a script consists of a sequence of statements applied to a stream of records. Each record is a shallow JSON-like structure — essentially, a collection of key-value pairs. A key is a string from a predefined set, and its value can be one of the primitive types: string, integer, boolean, or float. A record represents a genetic variant, and keys reflect the genetic **annotations** associated with the variant, such as provenance, biological, or clinical evidence.

The set of annotations, also known as keys, can be found
[here](../../app/config/dictionary/annotations.yml)

Annotations are classified based on their purpose as follows:

* Phenotype
* Provenance
* Evidence

Evidence annotations undergo further classification according to scale, knowledge domain, and method of acquisition.
Thus, each annotation possesses either one classification (when the purpose is `phenotype` or `provenance`) or four
classifications (`purpose`, `scale`, `knowledge domain`, and `method`) when it serves as evidence.

In a record, a tuple consisting of a key and value is referred to as a **variable**.

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

<Predicate> ::= (Logical expression in Python syntax that can use any variables in the record with `and`, `or`, `not`, etc.)

<Validation> ::= '"""' <newline> <Metapredicates> <newline> '"""'

<Metapredicates> ::= <Metapredicate>
                   | <Metapredicate> <newline> <Metapredicates>

<Metapredicate> ::= '@' <classification> '(' <classification_value> ')'

<classification> ::= "Purpose" 
                   | '"Knowledge Domain"'
                   | "knowledge_domain"
                   | "Scale" 
                   | "Method"
       (case-insensitive)

<classification_value> ::= (an arbitrary string value)
```

f a Metapredicates section is defined for a statement, then the logical expression is validated as follows:

For each Metapredicate, there must exist a variable within the logical expression such that its key (genetic annotation)
aligns with the classification specified by the Metapredicate.
