package com.salarytransparency.ui.fragments

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.salarytransparency.R
import com.salarytransparency.ui.adapters.SalaryEntryAdapter
import com.salarytransparency.viewmodel.SalaryViewModel
import java.text.NumberFormat
import java.util.*

class HomeFragment : Fragment() {
    
    private val viewModel: SalaryViewModel by activityViewModels()
    private lateinit var adapter: SalaryEntryAdapter
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_home, container, false)
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        val tvTotalEntries = view.findViewById<TextView>(R.id.tv_total_entries)
        val tvAverageSalary = view.findViewById<TextView>(R.id.tv_average_salary)
        val tvMedianSalary = view.findViewById<TextView>(R.id.tv_median_salary)
        val recyclerView = view.findViewById<RecyclerView>(R.id.rv_salary_entries)
        
        adapter = SalaryEntryAdapter()
        recyclerView.adapter = adapter
        recyclerView.layoutManager = LinearLayoutManager(requireContext())
        
        viewModel.filteredEntries.observe(viewLifecycleOwner) { entries ->
            adapter.submitList(entries)
        }
        
        viewModel.statistics.observe(viewLifecycleOwner) { stats ->
            val formatter = NumberFormat.getCurrencyInstance(Locale.US)
            tvTotalEntries.text = "Total Entries: ${stats.totalEntries}"
            tvAverageSalary.text = "Average Salary: ${formatter.format(stats.averageSalary)}"
            tvMedianSalary.text = "Median Salary: ${formatter.format(stats.medianSalary)}"
        }
    }
}
