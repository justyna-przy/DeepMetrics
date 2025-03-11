import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import styled from "styled-components";
import RowMetric from "../components/RowMetric";
import StyledDropdown from "../components/Dropdown";
import { config } from "../config/config";

const PageContainer = styled.div`
  width: calc(100% - 4rem);
  max-width: 87rem;
  margin: 2rem auto;
`;

const ControlRow = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: ${({ theme }) => theme.colors.header};
  padding: 0.75rem 1rem;
  border-radius: 0.75rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 1rem;
`;

const ControlGroup = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
`;

const LabelText = styled.span`
  margin-right: 0.5rem;
  font-weight: 600;
`;

const SummaryText = styled.div`
  font-weight: 500;
  margin-left: 1rem;
`;

const RowTable = styled.table`
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  border: 1px solid ${({ theme }) => theme.colors.header};
  border-radius: 0.75rem;
  background-color: ${({ theme }) => theme.colors.device_background};

  tbody tr:not(:last-child) {
    border-bottom: 1px solid ${({ theme }) => theme.colors.header};
  }

  tbody tr:nth-child(odd) {
    background-color: ${({ theme }) => theme.odd_row};
  }

  tbody tr:nth-child(even) {
    background-color: ${({ theme }) => theme.even_row};
  }
`;

const PaginationContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 1.5rem;
  gap: 0.5rem;
  padding: 0.5rem;
`;

const PageButton = styled.button`
  color: ${({ theme }) => theme.colors.text};
  padding: 0.5rem 1rem;
  border: 1px solid ${({ theme }) => theme.colors.header};
  background-color: ${({ theme }) => theme.colors.device_background};
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease, color 0.2s ease;

  &:hover:not(:disabled) {
    background-color: ${({ theme }) => theme.colors.header};
  }

  &:disabled {
    opacity: 0.5;
    cursor: default;
  }
`;

const MetricPage: React.FC = () => {
  // Extract metric name from route param, e.g. /metric/:metricName
  const { metricName } = useParams<{ metricName: string }>();

  // Local state for sort & time filters
  const [sortValue, setSortValue] = useState("desc");
  const [timeFilter, setTimeFilter] = useState("24h");

  // Data states
  const [rows, setRows] = useState<Array<{ timestamp: string; value: number }>>(
    []
  );
  const [averageValue, setAverageValue] = useState<number>(0);
  const [maxValue, setMaxValue] = useState<number>(0);

  // Pagination states
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [pageSize] = useState<number>(10); // adjust if needed
  const [totalCount, setTotalCount] = useState<number>(0);

  // Derived total pages
  const totalPages = Math.ceil(totalCount / pageSize) || 1;

  useEffect(() => {
    const fetchMetricHistory = async () => {
      if (!metricName) return;

      try {
        const params = new URLSearchParams({
          metric_name: metricName,
          time_filter: timeFilter,
          sort: sortValue,
          page: currentPage.toString(),
          page_size: pageSize.toString(),
        });

        const resp = await fetch(
          `${config.apiBaseUrl}${config.endpoints.metricsHistory}?${params}`
        );
        if (!resp.ok) {
          throw new Error(`Failed to fetch metric history: ${resp.statusText}`);
        }
        const data = await resp.json();

        // Populate state
        setRows(data.rows || []);
        setAverageValue(data.averageValue || 0);
        setMaxValue(data.maxValue || 0);
        setTotalCount(data.totalCount || 0);
      } catch (err) {
        console.error("Error fetching metric history:", err);
      }
    };

    fetchMetricHistory();
  }, [metricName, timeFilter, sortValue, currentPage, pageSize]);

  const handleSortChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSortValue(e.target.value);
    // Reset to first page when sort changes
    setCurrentPage(1);
  };

  const handleTimeFilterChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setTimeFilter(e.target.value);
    // Reset to first page on time filter change
    setCurrentPage(1);
  };

  const handlePrevPage = () => {
    setCurrentPage((prev) => Math.max(prev - 1, 1));
  };

  const handleNextPage = () => {
    setCurrentPage((prev) => Math.min(prev + 1, totalPages));
  };

  return (
    <PageContainer>
      <ControlRow>
        <ControlGroup>
          <div>
            <LabelText>Sort:</LabelText>
            <StyledDropdown value={sortValue} onChange={handleSortChange}>
              <option value="asc">Ascending</option>
              <option value="desc">Descending</option>
            </StyledDropdown>
          </div>
          <div>
            <LabelText>Filter:</LabelText>
            <StyledDropdown
              value={timeFilter}
              onChange={handleTimeFilterChange}
            >
              <option value="24h">Past 24 hours</option>
              <option value="7d">Past 7 days</option>
              <option value="30d">Past 30 days</option>
            </StyledDropdown>
          </div>
        </ControlGroup>
        <ControlGroup>
          <SummaryText>Average Value: {averageValue.toFixed(2)}</SummaryText>
          <SummaryText>Maximum Value: {maxValue.toFixed(2)}</SummaryText>
        </ControlGroup>
      </ControlRow>

      <RowTable>
        <tbody>
          {rows.map((row, idx) => (
            <RowMetric key={idx} metricName={row.timestamp} value={row.value} />
          ))}
        </tbody>
      </RowTable>

      <PaginationContainer>
        <PageButton disabled={currentPage === 1} onClick={handlePrevPage}>
          &lt;
        </PageButton>

        <span>
          Page {currentPage} of {totalPages}
        </span>

        <PageButton
          disabled={currentPage === totalPages}
          onClick={handleNextPage}
        >
          &gt;
        </PageButton>
      </PaginationContainer>
    </PageContainer>
  );
};

export default MetricPage;
