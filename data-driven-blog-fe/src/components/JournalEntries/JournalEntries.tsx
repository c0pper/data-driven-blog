import { useState, useEffect, use } from 'react';
import axios from 'axios';
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from '@/components/ui/pagination';

interface JournalEntry {
  id: string;
  title: string;
  content: string;
  entry_date: string;
  created_at: string;
  updated_at: string;
}

interface PaginationData {
  currentPage: number;
  totalPages: number;
  hasNext: boolean;
  hasPrevious: boolean;
}

const ITEMS_PER_PAGE = 10;

const JournalEntriesContainer = () => {
    const journalId = import.meta.env.VITE_JOURNAL_ID;
    const [entries, setEntries] = useState<JournalEntry[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [pagination, setPagination] = useState<PaginationData>({
        currentPage: 1,
        totalPages: 1,
        hasNext: false,
        hasPrevious: false,
    });

    const fetchEntries = async (page: number = 1) => {
    try {
        setLoading(true);
        
        const response = await axios.get(`http://localhost:8100/api/journal-entries/paginated`, {
        params: {
            journal_id: journalId, // Replace with actual journal ID
            page,
            limit: ITEMS_PER_PAGE,
        },
        });

        setEntries(response.data.entries);
        
        // Use the pagination data from the backend response
        setPagination({
        currentPage: response.data.pagination.currentPage,
        totalPages: response.data.pagination.totalPages,
        hasNext: response.data.pagination.hasNext,
        hasPrevious: response.data.pagination.hasPrevious,
        });
    } catch (err) {
        setError('Failed to fetch journal entries');
        console.error('Error fetching entries:', err);
    } finally {
        setLoading(false);
    }
    };

    useEffect(() => {
        fetchEntries(1);
    }, []);

    const handlePageChange = (page: number) => {
        if (page >= 1 && page <= pagination.totalPages) {
        fetchEntries(page);
        }
    };

    if (loading) {
        return (
        <div className="flex justify-center items-center p-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        </div>
        );
    }

    if (error) {
        return (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800">{error}</p>
            <button
            onClick={() => fetchEntries(1)}
            className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
            Retry
            </button>
        </div>
        );
    }

    return (
        <div className="space-y-6">
        <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold">Journal Entries</h2>
            <div className="text-sm text-gray-600">
            Page {pagination.currentPage} of {pagination.totalPages}
            </div>
        </div>

        {/* Entries List */}
        <div className="space-y-4">
            {entries.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
                No journal entries found.
            </div>
            ) : (
            entries.map((entry) => (
                <div
                key={entry.id}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                <h3 className="font-semibold text-lg mb-2">{entry.title}</h3>
                <p className="text-gray-600 mb-2 line-clamp-2">{entry.content}</p>
                <div className="flex justify-between text-sm text-gray-500">
                    <span>Date: {new Date(entry.entry_date).toLocaleDateString()}</span>
                    <span>Updated: {new Date(entry.updated_at).toLocaleDateString()}</span>
                </div>
                </div>
            ))
            )}
        </div>

        {/* Pagination */}
        {pagination.totalPages > 1 && (
            <Pagination>
            <PaginationContent>
                {/* Previous Button */}
                <PaginationItem>
                <PaginationPrevious
                    href="#"
                    onClick={(e) => {
                    e.preventDefault();
                    if (pagination.hasPrevious) {
                        handlePageChange(pagination.currentPage - 1);
                    }
                    }}
                    className={
                    !pagination.hasPrevious
                        ? 'pointer-events-none opacity-50'
                        : 'cursor-pointer'
                    }
                />
                </PaginationItem>

                {/* Page Numbers */}
                {Array.from({ length: pagination.totalPages }, (_, i) => i + 1).map(
                (page) => (
                    <PaginationItem key={page}>
                    <PaginationLink
                        href="#"
                        onClick={(e) => {
                        e.preventDefault();
                        handlePageChange(page);
                        }}
                        isActive={page === pagination.currentPage}
                        className="cursor-pointer"
                    >
                        {page}
                    </PaginationLink>
                    </PaginationItem>
                )
                )}

                {/* Next Button */}
                <PaginationItem>
                <PaginationNext
                    href="#"
                    onClick={(e) => {
                    e.preventDefault();
                    if (pagination.hasNext) {
                        handlePageChange(pagination.currentPage + 1);
                    }
                    }}
                    className={
                    !pagination.hasNext
                        ? 'pointer-events-none opacity-50'
                        : 'cursor-pointer'
                    }
                />
                </PaginationItem>
            </PaginationContent>
            </Pagination>
        )}
        </div>
    );
    };

    export default JournalEntriesContainer;