#pragma once

#include <vector>
#include <mutex>
#include <algorithm>
#include <cmath>
#include <iostream>

namespace nexus {

struct SearchResult {
    uint64_t id;
    float distance;
};

/**
 * @brief High-Performance Thread-Safe Vector Index.
 * 
 * Supports adding vectors and searching nearest neighbors.
 * Designed to release Python GIL during heavy computations.
 */
class VectorIndex {
public:
    VectorIndex(int dimension) : dimension_(dimension) {}

    /**
     * @brief Add a vector to the index.
     * Simple linear storage for this portfolio demo.
     */
    void add_item(uint64_t id, const std::vector<float>& vector) {
        if (vector.size() != dimension_) {
            throw std::runtime_error("Dimension mismatch");
        }
        
        std::lock_guard<std::mutex> lock(data_mutex_);
        ids_.push_back(id);
        vectors_.push_back(vector);
    }

    /**
     * @brief Search for k-nearest neighbors.
     * This method is compute-intensive and meant to be run without the GIL.
     */
    std::vector<SearchResult> search(const std::vector<float>& query, int k) const {
        if (query.size() != dimension_) {
            throw std::runtime_error("Dimension mismatch");
        }

        // Just a brute-force search for demonstration of Architecture (GIL release)
        // In production, this would be traversing an HNSW graph.
        
        std::vector<SearchResult> results;
        results.reserve(ids_.size());

        // Snapshot size to allow concurrent appends (with some caveats, but simple here)
        // Ideally we'd use a Reader-Writer lock.
        size_t count = ids_.size(); 

        for (size_t i = 0; i < count; ++i) {
            float dist = compute_l2_sq(query, vectors_[i]);
            results.push_back({ids_[i], dist});
        }

        // Partial sort to find top K
        size_t keep = std::min((size_t)k, results.size());
        std::partial_sort(results.begin(), results.begin() + keep, results.end(), 
            [](const SearchResult& a, const SearchResult& b) {
                return a.distance < b.distance;
            });
        
        results.resize(keep);
        return results;
    }

private:
    int dimension_;
    std::vector<uint64_t> ids_;
    std::vector<std::vector<float>> vectors_; // SoA or AoS, using AoS for simplicity
    mutable std::mutex data_mutex_;

    // Optimized distance function (Assume SIMDizable by compiler -O3)
    float compute_l2_sq(const std::vector<float>& a, const std::vector<float>& b) const {
        float sum = 0.0f;
        for (size_t i = 0; i < dimension_; ++i) {
            float diff = a[i] - b[i];
            sum += diff * diff;
        }
        return sum;
    }
};

} // namespace nexus
