package com.salarytransparency.data.model

data class FilterCriteria(
    val industries: List<String> = emptyList(),
    val locations: List<String> = emptyList(),
    val countries: List<String> = emptyList(),
    val minExperience: Int? = null,
    val maxExperience: Int? = null,
    val minSalary: Double? = null,
    val maxSalary: Double? = null,
    val educationLevels: List<String> = emptyList(),
    val genders: List<String> = emptyList()
)
