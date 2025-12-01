package com.salarytransparency.repository

import androidx.lifecycle.LiveData
import com.salarytransparency.data.dao.SalaryDao
import com.salarytransparency.data.model.FilterCriteria
import com.salarytransparency.data.model.SalaryEntry
import com.salarytransparency.data.model.StatisticsData
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class SalaryRepository(private val salaryDao: SalaryDao) {
    
    val allEntries: LiveData<List<SalaryEntry>> = salaryDao.getAllEntries()
    
    suspend fun insert(entry: SalaryEntry) = withContext(Dispatchers.IO) {
        salaryDao.insert(entry)
    }
    
    suspend fun insertAll(entries: List<SalaryEntry>) = withContext(Dispatchers.IO) {
        salaryDao.insertAll(entries)
    }
    
    suspend fun update(entry: SalaryEntry) = withContext(Dispatchers.IO) {
        salaryDao.update(entry)
    }
    
    suspend fun delete(entry: SalaryEntry) = withContext(Dispatchers.IO) {
        salaryDao.delete(entry)
    }
    
    suspend fun deleteAll() = withContext(Dispatchers.IO) {
        salaryDao.deleteAll()
    }
    
    suspend fun getAllEntriesList(): List<SalaryEntry> = withContext(Dispatchers.IO) {
        salaryDao.getAllEntriesSuspend()
    }
    
    suspend fun getFilteredEntries(criteria: FilterCriteria): List<SalaryEntry> = withContext(Dispatchers.IO) {
        var entries = salaryDao.getAllEntriesSuspend()
        
        if (criteria.industries.isNotEmpty()) {
            entries = entries.filter { it.industry in criteria.industries }
        }
        if (criteria.locations.isNotEmpty()) {
            entries = entries.filter { it.location in criteria.locations }
        }
        if (criteria.countries.isNotEmpty()) {
            entries = entries.filter { it.country in criteria.countries }
        }
        if (criteria.educationLevels.isNotEmpty()) {
            entries = entries.filter { it.educationLevel in criteria.educationLevels }
        }
        if (criteria.genders.isNotEmpty()) {
            entries = entries.filter { it.gender in criteria.genders }
        }
        if (criteria.minExperience != null) {
            entries = entries.filter { it.yearsOfExperience >= criteria.minExperience }
        }
        if (criteria.maxExperience != null) {
            entries = entries.filter { it.yearsOfExperience <= criteria.maxExperience }
        }
        if (criteria.minSalary != null) {
            entries = entries.filter { it.salaryUsd >= criteria.minSalary }
        }
        if (criteria.maxSalary != null) {
            entries = entries.filter { it.salaryUsd <= criteria.maxSalary }
        }
        
        entries
    }
    
    suspend fun getStatistics(entries: List<SalaryEntry>): StatisticsData = withContext(Dispatchers.IO) {
        if (entries.isEmpty()) {
            return@withContext StatisticsData(
                totalEntries = 0,
                averageSalary = 0.0,
                medianSalary = 0.0,
                minSalary = 0.0,
                maxSalary = 0.0,
                industryDistribution = emptyMap(),
                experienceDistribution = emptyMap(),
                educationDistribution = emptyMap(),
                genderDistribution = emptyMap()
            )
        }
        
        val salaries = entries.map { it.salaryUsd }.sorted()
        val median = if (salaries.size % 2 == 0) {
            (salaries[salaries.size / 2 - 1] + salaries[salaries.size / 2]) / 2
        } else {
            salaries[salaries.size / 2]
        }
        
        StatisticsData(
            totalEntries = entries.size,
            averageSalary = entries.map { it.salaryUsd }.average(),
            medianSalary = median,
            minSalary = salaries.first(),
            maxSalary = salaries.last(),
            industryDistribution = entries.groupBy { it.industry }.mapValues { it.value.size },
            experienceDistribution = entries.groupBy { 
                when(it.yearsOfExperience) {
                    in 0..2 -> "0-2 years"
                    in 3..5 -> "3-5 years"
                    in 6..10 -> "6-10 years"
                    else -> "10+ years"
                }
            }.mapValues { it.value.size },
            educationDistribution = entries.groupBy { it.educationLevel }.mapValues { it.value.size },
            genderDistribution = entries.groupBy { it.gender }.mapValues { it.value.size }
        )
    }
    
    suspend fun getAllIndustries(): List<String> = withContext(Dispatchers.IO) {
        salaryDao.getAllIndustries()
    }
    
    suspend fun getAllLocations(): List<String> = withContext(Dispatchers.IO) {
        salaryDao.getAllLocations()
    }
    
    suspend fun getAllCountries(): List<String> = withContext(Dispatchers.IO) {
        salaryDao.getAllCountries()
    }
    
    suspend fun getAllEducationLevels(): List<String> = withContext(Dispatchers.IO) {
        salaryDao.getAllEducationLevels()
    }
}
