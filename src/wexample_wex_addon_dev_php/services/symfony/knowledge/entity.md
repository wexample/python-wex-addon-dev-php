A Symfony entity must extend, directly or indirectly, the abstract class
`Wexample\SymfonyHelpers\Entity\AbstractEntity`. It provides the `id` column, the
`BaseEntityTrait` and the entity naming/path helpers the rest of the framework relies
on — an entity that does not extend it is not wired into those conventions.