package edu.example.mobilecourse

data class CourseTask(
    val id: Int,
    val title: String,
    val owner: String?,
    val completed: Boolean = false
) {
    fun displayOwner(): String =
        owner?.trim()?.takeIf { it.isNotEmpty() } ?: "未指派"
}
