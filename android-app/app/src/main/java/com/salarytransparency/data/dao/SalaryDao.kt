package com.salarytransparency.data.dao

import androidx.lifecycle.LiveData
import androidx.room.*
import com.salarytransparency.data.model.SalaryEntry

@Dao
interface SalaryDao {
    @Query("SELECT * FROM salary_entries ORDER BY submissionDate DESC")
    fun getAllEntries(): LiveData<List<SalaryEntry>>
    
    @Query("SELECT * FROM salary_entries ORDER BY submissionDate DESC")
    suspend fun getAllEntriesSuspend(): List<SalaryEntry>
    
    @Query("SELECT * FROM salary_entries WHERE id = :id")
    suspend fun getEntryById(id: Long): SalaryEntry?
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(entry: SalaryEntry): Long
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(entries: List<SalaryEntry>)
    
    @Update
    suspend fun update(entry: SalaryEntry)
    
    @Delete
    suspend fun delete(entry: SalaryEntry)
    
    @Query("DELETE FROM salary_entries")
    suspend fun deleteAll()
    
    @Query("SELECT DISTINCT industry FROM salary_entries ORDER BY industry")
    suspend fun getAllIndustries(): List<String>
    
    @Query("SELECT DISTINCT location FROM salary_entries ORDER BY location")
    suspend fun getAllLocations(): List<String>
    
    @Query("SELECT DISTINCT country FROM salary_entries ORDER BY country")
    suspend fun getAllCountries(): List<String>
    
    @Query("SELECT DISTINCT educationLevel FROM salary_entries ORDER BY educationLevel")
    suspend fun getAllEducationLevels(): List<String>
    
    @Query("SELECT AVG(salaryUsd) FROM salary_entries")
    suspend fun getAverageSalary(): Double?
    
    @Query("SELECT COUNT(*) FROM salary_entries")
    suspend fun getEntryCount(): Int
}
