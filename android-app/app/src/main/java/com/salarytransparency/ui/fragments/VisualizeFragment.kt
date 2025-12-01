package com.salarytransparency.ui.fragments

import android.graphics.Color
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import com.github.mikephil.charting.charts.BarChart
import com.github.mikephil.charting.charts.LineChart
import com.github.mikephil.charting.charts.PieChart
import com.github.mikephil.charting.components.XAxis
import com.github.mikephil.charting.data.*
import com.github.mikephil.charting.formatter.IndexAxisValueFormatter
import com.github.mikephil.charting.utils.ColorTemplate
import com.salarytransparency.R
import com.salarytransparency.viewmodel.SalaryViewModel

class VisualizeFragment : Fragment() {
    
    private val viewModel: SalaryViewModel by activityViewModels()
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_visualize, container, false)
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        val barChart = view.findViewById<BarChart>(R.id.chart_salary_by_industry)
        val lineChart = view.findViewById<LineChart>(R.id.chart_salary_by_experience)
        val genderPieChart = view.findViewById<PieChart>(R.id.chart_gender_distribution)
        val industryPieChart = view.findViewById<PieChart>(R.id.chart_industry_distribution)
        
        viewModel.statistics.observe(viewLifecycleOwner) { stats ->
            setupBarChart(barChart, stats.industryDistribution)
            setupLineChart(lineChart, stats.experienceDistribution)
            setupPieChart(genderPieChart, stats.genderDistribution, "Gender Distribution")
            setupPieChart(industryPieChart, stats.industryDistribution, "Industry Distribution")
        }
    }
    
    private fun setupBarChart(chart: BarChart, data: Map<String, Int>) {
        val entries = data.entries.mapIndexed { index, entry ->
            BarEntry(index.toFloat(), entry.value.toFloat())
        }
        
        val dataSet = BarDataSet(entries, "Count by Industry")
        dataSet.colors = ColorTemplate.MATERIAL_COLORS.toList()
        
        val barData = BarData(dataSet)
        chart.data = barData
        
        chart.xAxis.valueFormatter = IndexAxisValueFormatter(data.keys.toList())
        chart.xAxis.position = XAxis.XAxisPosition.BOTTOM
        chart.xAxis.granularity = 1f
        chart.axisRight.isEnabled = false
        chart.description.text = "Salary Distribution by Industry"
        chart.animateY(1000)
        chart.invalidate()
    }
    
    private fun setupLineChart(chart: LineChart, data: Map<String, Int>) {
        val entries = data.entries.mapIndexed { index, entry ->
            Entry(index.toFloat(), entry.value.toFloat())
        }
        
        val dataSet = LineDataSet(entries, "Count by Experience")
        dataSet.color = Color.BLUE
        dataSet.valueTextColor = Color.BLACK
        dataSet.lineWidth = 2f
        dataSet.circleRadius = 4f
        
        val lineData = LineData(dataSet)
        chart.data = lineData
        
        chart.xAxis.valueFormatter = IndexAxisValueFormatter(data.keys.toList())
        chart.xAxis.position = XAxis.XAxisPosition.BOTTOM
        chart.xAxis.granularity = 1f
        chart.axisRight.isEnabled = false
        chart.description.text = "Distribution by Experience"
        chart.animateX(1000)
        chart.invalidate()
    }
    
    private fun setupPieChart(chart: PieChart, data: Map<String, Int>, label: String) {
        val entries = data.map { PieEntry(it.value.toFloat(), it.key) }
        
        val dataSet = PieDataSet(entries, label)
        dataSet.colors = ColorTemplate.COLORFUL_COLORS.toList()
        dataSet.valueTextSize = 12f
        dataSet.valueTextColor = Color.BLACK
        
        val pieData = PieData(dataSet)
        chart.data = pieData
        
        chart.description.text = label
        chart.centerText = label
        chart.setCenterTextSize(16f)
        chart.animateY(1000)
        chart.invalidate()
    }
}
