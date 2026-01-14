# Implementation Plan: ServiceNow MCP Server

## Overview

This implementation plan breaks down the ServiceNow MCP Server into discrete coding tasks using Python and **FastMCP 2.0**. FastMCP 2.0 simplifies MCP server development by handling protocol boilerplate through decorators, allowing focus on ServiceNow integration logic. The approach builds from core components up to decorated tools that expose ServiceNow functionality.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create Python package structure with proper modules
  - Set up pyproject.toml with FastMCP 2.0 and required dependencies (fastmcp, requests, pydantic, python-dotenv)
  - Create configuration management for ServiceNow credentials
  - Set up logging and basic error handling framework
  - _Requirements: 8.1, 8.2, 8.3_

- [x] 2. Implement ServiceNow client and authentication
  - [x] 2.1 Create ServiceNow credentials and configuration models
    - Implement Pydantic models for credentials and configuration
    - Add support for environment variable loading
    - _Requirements: 8.1, 8.2, 8.4_

  - [ ]* 2.2 Write property test for configuration management
    - **Property 9: Configuration Management Robustness**
    - **Validates: Requirements 8.1, 8.2, 8.3, 8.5**

  - [x] 2.3 Implement ServiceNow HTTP client with authentication
    - Create ServiceNowClient class with authentication methods
    - Implement basic auth and API key authentication
    - Add connection validation and timeout handling
    - _Requirements: 1.1, 1.4, 1.5, 8.4_

  - [ ]* 2.4 Write property test for authentication validation
    - **Property 1: Authentication Validation**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5**

- [x] 3. Implement core ServiceNow operations
  - [x] 3.1 Implement Service Request creation functionality
    - Add create_request method with field validation
    - Handle ServiceNow API responses and error parsing
    - _Requirements: 2.1, 2.3, 2.4, 2.5_

  - [ ]* 3.2 Write property test for Service Request creation
    - **Property 2: Service Request Creation Round Trip**
    - **Validates: Requirements 2.1, 2.3, 2.4**

  - [x] 3.3 Implement Service Request retrieval functionality
    - Add get_request method supporting both sys_id and request number
    - Ensure complete field retrieval including timestamps and status
    - _Requirements: 3.1, 3.2, 3.4_

  - [ ]* 3.4 Write property test for Service Request retrieval
    - **Property 4: Service Request Retrieval Consistency**
    - **Validates: Requirements 3.1, 3.2, 3.4**

  - [x] 3.5 Implement Service Request update functionality
    - Add update_request method with field validation
    - Support updating state, priority, assignment_group, and work_notes
    - _Requirements: 4.1, 4.4, 4.5_

  - [ ]* 3.6 Write property test for Service Request updates
    - **Property 5: Update Operation Consistency**
    - **Validates: Requirements 4.1, 4.4, 4.5**

- [x] 4. Checkpoint - Ensure ServiceNow operations work
  - Ensure all tests pass, ask the user if questions arise.

- [-] 5. Implement search and filtering functionality
  - [x] 5.1 Implement Service Request search with multiple criteria
    - Add search_requests method supporting status, user, and date filters
    - Implement AND logic for combining multiple criteria
    - Handle empty result sets appropriately
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [ ]* 5.2 Write property test for search functionality
    - **Property 6: Search Filter Accuracy**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**

- [ ] 6. Implement comprehensive error handling
  - [ ] 6.1 Add error handling for all ServiceNow API scenarios
    - Handle HTTP status codes, rate limits, and network errors
    - Parse ServiceNow error messages and provide clear guidance
    - Add retry logic with configurable settings
    - _Requirements: 6.1, 6.2, 6.3, 6.5_

  - [ ]* 6.2 Write property test for error handling
    - **Property 7: Error Handling Consistency**
    - **Validates: Requirements 2.5, 3.3, 4.2, 6.1, 6.2, 6.3, 6.5**

  - [ ] 6.3 Implement input validation for all operations
    - Add parameter validation before ServiceNow API calls
    - Validate required fields and data types
    - _Requirements: 2.2, 4.3, 6.4_

  - [ ]* 6.4 Write property test for input validation
    - **Property 3: Input Validation Consistency**
    - **Validates: Requirements 2.2, 4.3, 6.4, 7.3**

- [ ] 7. Implement FastMCP tools for ServiceNow operations
  - [ ] 7.1 Create FastMCP server instance and tool decorators
    - Initialize FastMCP server with proper configuration
    - Create @mcp.tool decorated functions for all ServiceNow operations
    - Implement automatic schema generation from function signatures
    - _Requirements: 7.1, 7.2_

  - [ ] 7.2 Wire FastMCP tools to ServiceNow client methods
    - Connect decorated tools to ServiceNow client operations
    - Implement proper error handling and response formatting
    - Ensure FastMCP protocol compliance through framework
    - _Requirements: 7.1, 7.4, 7.5_

  - [ ]* 7.3 Write property test for FastMCP protocol compliance
    - **Property 8: MCP Protocol Compliance**
    - **Validates: Requirements 7.1, 7.2, 7.4, 7.5**

- [ ] 8. Integration and server startup
  - [ ] 8.1 Create main server entry point with FastMCP
    - Implement server startup using FastMCP.run() method
    - Add graceful shutdown and connection management
    - Configure FastMCP server with ServiceNow client integration
    - _Requirements: 1.1, 8.1, 8.2, 8.3_

  - [ ]* 8.2 Write integration tests for end-to-end workflows
    - Test complete FastMCP tool execution through ServiceNow API
    - Test error propagation across all layers using FastMCP testing utilities
    - _Requirements: All requirements_

- [ ] 9. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties using Hypothesis
- Unit tests validate specific examples and edge cases
- The implementation uses **FastMCP 2.0** for simplified MCP server development with decorators
- FastMCP 2.0 handles MCP protocol boilerplate, tool discovery, and schema generation automatically
- ServiceNow integration uses Requests for HTTP communication and Pydantic for data validation