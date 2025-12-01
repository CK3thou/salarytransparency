package com.salarytransparency.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import com.salarytransparency.data.database.SalaryDatabase
import com.salarytransparency.data.model.FilterCriteria
import com.salarytransparency.data.model.SalaryEntry
import com.salarytransparency.data.model.StatisticsData
import com.salarytransparency.repository.SalaryRepository
import kotlinx.coroutines.launch

class SalaryViewModel(application: Application) : AndroidViewModel(application) {
    private val repository: SalaryRepository
    val allEntries: LiveData<List<SalaryEntry>>
    
    private val _filteredEntries = MutableLiveData<List<SalaryEntry>>()
    val filteredEntries: LiveData<List<SalaryEntry>> = _filteredEntries
    
    private val _statistics = MutableLiveData<StatisticsData>()
    val statistics: LiveData<StatisticsData> = _statistics
    
    private val _filterCriteria = MutableLiveData(FilterCriteria())
    val filterCriteria: LiveData<FilterCriteria> = _filterCriteria
    
    private val _industries = MutableLiveData<List<String>>()
    val industries: LiveData<List<String>> = _industries
    
    private val _locations = MutableLiveData<List<String>>()
    val locations: LiveData<List<String>> = _locations
    
    private val _countries = MutableLiveData<List<String>>()
    val countries: LiveData<List<String>> = _countries
    
    private val _educationLevels = MutableLiveData<List<String>>()
    val educationLevels: LiveData<List<String>> = _educationLevels
    
    init {
        val salaryDao = SalaryDatabase.getDatabase(application).salaryDao()
        repository = SalaryRepository(salaryDao)
        allEntries = repository.allEntries
        
        loadFilterOptions()
        applyFilters()
    }
    
    fun insert(entry: SalaryEntry) = viewModelScope.launch {
        repository.insert(entry)
        loadFilterOptions()
        applyFilters()
    }
    
    fun insertAll(entries: List<SalaryEntry>) = viewModelScope.launch {
        repository.insertAll(entries)
        loadFilterOptions()
        applyFilters()
    }
    
    fun update(entry: SalaryEntry) = viewModelScope.launch {
        repository.update(entry)
        applyFilters()
    }
    
    fun delete(entry: SalaryEntry) = viewModelScope.launch {
        repository.delete(entry)
        applyFilters()
    }
    
    fun updateFilterCriteria(criteria: FilterCriteria) {
        _filterCriteria.value = criteria
        applyFilters()
    }
    
    fun clearFilters() {
        _filterCriteria.value = FilterCriteria()
        applyFilters()
    }
    
    private fun applyFilters() = viewModelScope.launch {
        val criteria = _filterCriteria.value ?: FilterCriteria()
        val filtered = repository.getFilteredEntries(criteria)
        _filteredEntries.value = filtered
        _statistics.value = repository.getStatistics(filtered)
    }
    
    private fun loadFilterOptions() = viewModelScope.launch {
        _industries.value = repository.getAllIndustries()
        _locations.value = repository.getAllLocations()
        _countries.value = repository.getAllCountries()
        _educationLevels.value = repository.getAllEducationLevels()
    }
    
    fun exportToCsv(): List<SalaryEntry> {
        return _filteredEntries.value ?: emptyList()
    }
}
