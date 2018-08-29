"""This module tests the ancestral_reconstruction/lm_objects/tree.py module

The functions in this module are pytest style tests for the tree.py module
"""
import dendropy
import pytest
import random

from ancestral_reconstruction.lm_objects import tree


# .............................................................................
class Test_PhyloTreeKeys(object):
    """Test the PhyloTreeKeys class

    This is a simple class that really just contains constants
    """
    # .....................................
    def test_get_constants(self):
        """Test that the constants can be retrieved
        """
        assert tree.PhyloTreeKeys.MTX_IDX is not None
        assert tree.PhyloTreeKeys.SQUID is not None


# .............................................................................
class Test_LmTreeException(object):
    """Test the LmException class
    """
    # .....................................
    def test_exception(self):
        """Attempt to throw the exception
        """
        with pytest.raises(tree.LmTreeException):
            raise tree.LmTreeException('Test exception')


# .............................................................................
class Test_TreeWrapper(object):
    """Test the TreeWrapper class

    The TreeWrapper class is an extension of dendropy.Tree.  Test that the
    functions do not break the existing functionality of the class and that
    they work properly
    """
    # .....................................
    def test_from_base_tree(self, data_files):
        """Attempt to get a tree using Dendropy and then wrap it

        Try to retrieve a tree using Dendropy and then send it through the
        wrapper function to determine if it produces a correctly wrapped tree
        """
        schemas = ['newick', 'nexus']
        for schema in schemas:
            for tree_filename in data_files.get_trees(schema, True):
                dendropy_tree = dendropy.Tree.get(path=tree_filename,
                                                  schema=schema)
                wrapped_tree = tree.TreeWrapper.from_base_tree(dendropy_tree)
                assert isinstance(wrapped_tree, tree.TreeWrapper)

    # .....................................
    def test_add_node_labels_no_prefix_no_overwrite(self):
        """Test that node labels are added correctly to a tree

        Attempt to add node labels without a prefix.  Any existing labels
        should be retained
        """
        newick_string = '(A,((B,C)testnode,(G,(D,(E,F)))));'
        existing_labels = ['A', 'B', 'C', 'testnode', 'G', 'D', 'E', 'F']
        my_tree = tree.TreeWrapper.get(data=newick_string, schema='newick')

        # Add node labels - Should all be integers
        my_tree.add_node_labels()

        for node in my_tree.nodes():
            if node.label is not None:
                label = node.label
            else:
                label = node.taxon.label
            # Check if the node label is in the existing labels
            if label in existing_labels:
                # Remove the label so we can verify that they were maintained
                existing_labels.pop(existing_labels.index(label))
            else:
                # Check that the label is the correct format
                assert str(int(label)) == label

        # Now verify that all of the previous labels were maintained
        assert len(existing_labels) == 0

    # .....................................
    def test_add_node_labels_with_prefix_no_overwrite(self):
        """Test that node labels are added correctly to a tree

        Attempt to add node labels with a prefix.  Any existing labels should
        be retained
        """
        node_prefix = 'nd_'
        newick_string = '(A,((B,C)testnode,(G,(D,(E,F)))));'
        existing_labels = ['A', 'B', 'C', 'testnode', 'G', 'D', 'E', 'F']
        my_tree = tree.TreeWrapper.get(data=newick_string, schema='newick')

        # Add node labels - Should all be integers
        my_tree.add_node_labels(prefix=node_prefix)

        for node in my_tree.nodes():
            if node.label is not None:
                label = node.label
            else:
                label = node.taxon.label
            # Check if the node label is in the existing labels
            if label in existing_labels:
                # Remove the label so we can verify that they were maintained
                existing_labels.pop(existing_labels.index(label))
            else:
                # Check that the label is the correct format
                assert label.startswith(node_prefix)
                # Check that we can create an integer from the suffix
                _ = int(label.strip(node_prefix))

        # Now verify that all of the previous labels were maintained
        assert len(existing_labels) == 0

    # .....................................
    def test_add_node_labels_no_prefix_yes_overwrite(self):
        """Test that node labels are added correctly to a tree

        Attempt to add node labels without a prefix.  Any existing node labels
        should not be retained
        """
        newick_string = '(A,((B,C)testnode,(G,(D,(E,F)))));'
        existing_labels = ['A', 'B', 'C', 'testnode', 'G', 'D', 'E', 'F']
        node_labels = ['testnode']  # Should not exist in modified version
        my_tree = tree.TreeWrapper.get(data=newick_string, schema='newick')

        # Add node labels - Should all be integers
        my_tree.add_node_labels(overwrite=True)

        for node in my_tree.nodes():
            if node.label is not None:
                label = node.label
            else:
                label = node.taxon.label
            # Check if the node label is in the existing labels
            if label in existing_labels:
                # Remove the label so we can verify that they were maintained
                existing_labels.pop(existing_labels.index(label))
            else:
                # Check that the label is the correct format
                assert str(int(label)) == label

        # Now verify that existing node labels were changed
        assert len(existing_labels) == len(node_labels)
        for node_label in existing_labels:
            assert node_label in node_labels

        for node_label in node_labels:
            assert node_label in existing_labels

    # .....................................
    def test_add_node_labels_with_prefix_yes_overwrite(self):
        """Test that node labels are added correctly to a tree

        Attempt to add node labels with a prefix.  Any existing labels should
        not be retained
        """
        node_prefix = 'nd_'
        newick_string = '(A,((B,C)testnode,(G,(D,(E,F)))));'
        existing_labels = ['A', 'B', 'C', 'testnode', 'G', 'D', 'E', 'F']
        node_labels = ['testnode']  # Should not exist in modified version
        my_tree = tree.TreeWrapper.get(data=newick_string, schema='newick')

        # Add node labels - Should all be integers
        my_tree.add_node_labels(prefix=node_prefix, overwrite=True)

        for node in my_tree.nodes():
            if node.label is not None:
                label = node.label
            else:
                label = node.taxon.label
            # Check if the node label is in the existing labels
            if label in existing_labels:
                # Remove the label so we can verify that they were maintained
                existing_labels.pop(existing_labels.index(label))
            else:
                # Check that the label is the correct format
                assert label.startswith(node_prefix)
                # Check that we can create an integer from the suffix
                _ = int(label.strip(node_prefix))

        # Now verify that existing node labels were changed
        assert len(existing_labels) == len(node_labels)
        for node_label in existing_labels:
            assert node_label in node_labels

        for node_label in node_labels:
            assert node_label in existing_labels

    # .....................................
    def test_annotate_tree_with_attribute_no_update(self):
        """Test annotate_tree with attribute as label, no updates

        Test that annotating the tree using an attribute label and not updating
        the existing attribute works properly.
        """
        # Set up tree
        nexus_string = """\
#NEXUS

BEGIN TAXA;
    DIMENSIONS NTAX=3;
    TAXLABELS
        Taxon_1
[&myatt=value1,&att2=existingvalue]
        Taxon_2
[&myatt=value2]
        Taxon_3
[&myatt=value3]
  ;
END;

BEGIN TREES;
    TREE 1 = (Taxon_1:0.2,(Taxon_2:0.1,Taxon_3:0.1):0.1);
END;
"""
        my_tree = tree.TreeWrapper.get(data=nexus_string, schema='nexus')
        # Set up attribute pairs
        att_pairs = {
            'value1': 't1_value',
            'value2': 't2_value',
            'value3': 't3_value'
        }

        check_pairs = {
            'Taxon 1': 't1_value',  # Should not be changed to this
            'Taxon 2': 't2_value',
            'Taxon 3': 't3_value'
        }

        # Get original annotations
        orig_annotations = dict(my_tree.get_annotations('att2'))

        # Annotate tree
        my_tree.annotate_tree('att2', att_pairs, label_attribute='myatt')

        # Check that annotations are correct
        annotations = my_tree.get_annotations('att2')

        for label, att in annotations:
            # Check that the label exists
            assert label in check_pairs.keys()
            # Check that if there was an original annotation, it was retained
            if orig_annotations[label] is not None:
                assert att == orig_annotations[label]
            else:
                # Check that the annotation is in the new annotation
                assert check_pairs[label] == att

    # .....................................
    def test_annotate_tree_with_attribute_yes_update(self):
        """Test annotate_tree with attribute as label, update existing

        Test that annotating the tree using an attribute label and updating
        the existing attribute works properly.
        """
        # Set up tree
        nexus_string = """\
#NEXUS

BEGIN TAXA;
    DIMENSIONS NTAX=3;
    TAXLABELS
        Taxon_1
[&myatt=value1,&att2=existingvalue]
        Taxon_2
[&myatt=value2]
        Taxon_3
[&myatt=value3]
  ;
END;

BEGIN TREES;
    TREE 1 = (Taxon_1:0.2,(Taxon_2:0.1,Taxon_3:0.1):0.1);
END;
"""
        my_tree = tree.TreeWrapper.get(data=nexus_string, schema='nexus')
        # Set up attribute pairs
        att_pairs = {
            'value1': 't1_value',
            'value2': 't2_value',
            'value3': 't3_value'
        }

        check_pairs = {
            'Taxon 1': 't1_value',  # Should not be changed to this
            'Taxon 2': 't2_value',
            'Taxon 3': 't3_value'
        }

        # Get original annotations
        orig_annotations = dict(my_tree.get_annotations('att2'))

        # Annotate tree
        my_tree.annotate_tree('att2', att_pairs, label_attribute='myatt',
                              update=True)

        # Check that annotations are correct
        annotations = my_tree.get_annotations('att2')

        for label, att in annotations:
            # Check that the label exists
            assert label in check_pairs.keys()
            # Check that the annotation is in the new annotation
            assert check_pairs[label] == att

    # .....................................
    def test_annotate_tree_with_bad_attribute(self):
        """Test annotate_tree when trying to use a bad label attribute

        Test that annotate_tree operates correctly when trying to add
        annotations based on a label attribute that does not exist
        """
        # Set up tree
        nexus_string = """\
#NEXUS

BEGIN TAXA;
    DIMENSIONS NTAX=3;
    TAXLABELS
        Taxon_1
        Taxon_2
        Taxon_3
  ;
END;

BEGIN TREES;
    TREE 1 = (Taxon_1:0.2,(Taxon_2:0.1,Taxon_3:0.1):0.1);
END;
"""
        my_tree = tree.TreeWrapper.get(data=nexus_string, schema='nexus')
        # Set up attribute pairs
        att_pairs = {
            'Taxon 1': 't1_value',
            'Taxon 2': 't2_value',
            'Taxon 3': 't3_value'
        }

        # Get original annotations
        orig_annotations = dict(my_tree.get_annotations('myatt'))

        # Annotate tree
        my_tree.annotate_tree('myatt', att_pairs, label_attribute='badatt')

        # Check that annotations are correct
        annotations = my_tree.get_annotations('myatt')

        for label, att in annotations:
            # Since the label attribute was bad, no annotations should change
            assert label in att_pairs.keys()
            # Check that if there was an original annotation, it was retained
            if orig_annotations[label] is not None:
                assert att == orig_annotations[label]
            else:
                # Check that the annotation has not been updated
                assert att_pairs[label] != att

    # .....................................
    def test_annotate_tree_with_label_no_update(self):
        """Test annotate_tree without updating existing values
        """
        # Set up tree
        nexus_string = """\
#NEXUS

BEGIN TAXA;
    DIMENSIONS NTAX=3;
    TAXLABELS
        Taxon_1
[&myatt=value1]
        Taxon_2
        Taxon_3
  ;
END;

BEGIN TREES;
    TREE 1 = (Taxon_1:0.2,(Taxon_2:0.1,Taxon_3:0.1):0.1);
END;
"""
        my_tree = tree.TreeWrapper.get(data=nexus_string, schema='nexus')
        # Set up attribute pairs
        att_pairs = {
            'Taxon 1': 't1_value',
            'Taxon 2': 't2_value',
            'Taxon 3': 't3_value'
        }

        # Get original annotations
        orig_annotations = dict(my_tree.get_annotations('myatt'))

        # Annotate tree
        my_tree.annotate_tree('myatt', att_pairs)

        # Check that annotations are correct
        annotations = my_tree.get_annotations('myatt')

        for label, att in annotations:
            # Check that the label exists
            assert label in att_pairs.keys()
            # Check that if there was an original annotation, it was retained
            if orig_annotations[label] is not None:
                assert att == orig_annotations[label]
            else:
                # Check that the annotation is in the new annotation
                assert att_pairs[label] == att

    # .....................................
    def test_annotate_tree_with_label_yes_update(self):
        """Test annotate_tree when updating existing values
        """
        # Set up tree
        nexus_string = """\
#NEXUS

BEGIN TAXA;
    DIMENSIONS NTAX=4;
    TAXLABELS
        Taxon_1
[&myatt=value1]
        Taxon_2
        Taxon_3
        Taxon_4
  ;
END;

BEGIN TREES;
    TREE 1 = ((Taxon_1:0.2,Taxon_4:02):0.0,(Taxon_2:0.1,Taxon_3:0.1):0.1);
END;
"""
        my_tree = tree.TreeWrapper.get(data=nexus_string, schema='nexus')
        # Set up attribute pairs
        att_pairs = {
            'Taxon 1': 't1_value',
            'Taxon 2': 't2_value',
            'Taxon 3': 't3_value'
        }

        # Get original annotations
        orig_annotations = dict(my_tree.get_annotations('myatt'))

        # Annotate tree
        my_tree.annotate_tree('myatt', att_pairs, update=True)

        # Check that annotations are correct
        annotations = my_tree.get_annotations('myatt')

        for label, att in annotations:
            # Check that the label exists
            if label in att_pairs.keys():
                assert label in att_pairs.keys()
                # Check that if there was an original annotation it was changed
                if orig_annotations[label] is not None:
                    assert att != orig_annotations[label]

                # Check that the annotation is in the new annotation
                assert att_pairs[label] == att
            else:
                # if the taxon was not annotated, this value should be None
                assert att is None

    # .....................................
    def test_get_annotations_bad_attribute(self):
        """Test get_annotations with an attribute that does not exist

        Test that retrieving annotations for an annotation attribute that does
        not exist returns None for each taxon.
        """
        # Set up tree
        nexus_string = """\
#NEXUS

BEGIN TAXA;
    DIMENSIONS NTAX=3;
    TAXLABELS
        Taxon_1
[&myatt=value1,&att2=existingvalue]
        Taxon_2
[&myatt=value2]
        Taxon_3
[&myatt=value3]
  ;
END;

BEGIN TREES;
    TREE 1 = (Taxon_1:0.2,(Taxon_2:0.1,Taxon_3:0.1):0.1);
END;
"""
        my_tree = tree.TreeWrapper.get(data=nexus_string, schema='nexus')

        # Get annotations
        annotations = my_tree.get_annotations('badattribute')

        for val, att in annotations:
            assert att is None

    # .....................................
    def test_get_annotations_good_attribute(self):
        """Test get_annotations with an attribute

        Test that retrieving annotations for an attribute works properly
        """
        # Set up tree
        nexus_string = """\
#NEXUS

BEGIN TAXA;
    DIMENSIONS NTAX=3;
    TAXLABELS
        Taxon_1
[&myatt=value1,&att2=existingvalue]
        Taxon_2
[&myatt=value2]
        Taxon_3
[&myatt=value3]
  ;
END;

BEGIN TREES;
    TREE 1 = (Taxon_1:0.2,(Taxon_2:0.1,Taxon_3:0.1):0.1);
END;
"""
        my_tree = tree.TreeWrapper.get(data=nexus_string, schema='nexus')

        # Get annotations
        annotations = my_tree.get_annotations('myatt')
        for val, att in annotations:
            assert att is not None

    # .....................................
    def test_get_distance_matrix_dendropy_with_attribute(self):
        """Test the get_distance_matrix_dendropy method using attribute labels

        Tests that the distance matrix generated by the
        get_distance_matrix_dendropy method is as expected when using attribute
        labels for the headers
        """
        # Set up tree
        nexus_string = """\
#NEXUS

BEGIN TAXA;
    DIMENSIONS NTAX=4;
    TAXLABELS
        Taxon_1
[&myatt=value1]
        Taxon_2
[&myatt=value2]
        Taxon_3
[&myatt=value3]
        Taxon_4
[&myatt=value4]
  ;
END;

BEGIN TREES;
    TREE 1 = ((Taxon_1:0.2,Taxon_4:0.2):0.1,(Taxon_2:0.1,Taxon_3:0.1):0.2);
END;
"""
        distance_sum = 6.0
        taxon_labels = ['value1', 'value2', 'value3', 'value4']
        my_tree = tree.TreeWrapper.get(data=nexus_string, schema='nexus')

        # Get default ordered distance matrix
        default_order_matrix = my_tree.get_distance_matrix_dendropy(
            label_attribute='myatt')
        def_col_headers = default_order_matrix.get_column_headers()
        def_row_headers = default_order_matrix.get_row_headers()

        # Ensure that headers are in the same order
        for i in range(len(taxon_labels)):
            assert def_col_headers[i] == def_row_headers[i]

        # Check the sum of the distance matrix, should be = ?
        assert default_order_matrix.data.sum() == distance_sum

        # Shuffle taxon labels and use them to order return matrix
        random.shuffle(taxon_labels)
        # Get the ordered distance matrix
        ordered_matrix = my_tree.get_distance_matrix_dendropy(
            label_attribute='myatt', ordered_labels=taxon_labels)
        ord_col_headers = ordered_matrix.get_column_headers()
        ord_row_headers = ordered_matrix.get_row_headers()

        # Ensure that headers are in the same order and match shuffled taxon
        #    labels
        for i in range(len(taxon_labels)):
            assert ord_col_headers[i] == ord_row_headers[i]
            assert ord_col_headers[i] == taxon_labels[i]

        # Check the sum of the distance matrix, should be = ?
        assert ordered_matrix.data.sum() == distance_sum

    # .....................................
    def test_get_distance_matrix_dendropy_with_label(self):
        """Test the get_distance_matrix_dendropy method using taxon labels

        Tests that the distance matrix generated by the
        get_distance_matrix_dendropy method is as expected when using taxon
        labels for the headers
        """
        # Set up tree
        nexus_string = """\
#NEXUS

BEGIN TAXA;
    DIMENSIONS NTAX=4;
    TAXLABELS
        Taxon_1
[&myatt=value1]
        Taxon_2
[&myatt=value2]
        Taxon_3
[&myatt=value3]
        Taxon_4
[&myatt=value4]
  ;
END;

BEGIN TREES;
    TREE 1 = ((Taxon_1:0.2,Taxon_4:0.2):0.1,(Taxon_2:0.1,Taxon_3:0.1):0.2);
END;
"""
        distance_sum = 6.0
        taxon_labels = ['Taxon 1', 'Taxon 2', 'Taxon 3', 'Taxon 4']
        my_tree = tree.TreeWrapper.get(data=nexus_string, schema='nexus')

        # Get default ordered distance matrix
        default_order_matrix = my_tree.get_distance_matrix_dendropy()
        def_col_headers = default_order_matrix.get_column_headers()
        def_row_headers = default_order_matrix.get_row_headers()

        # Ensure that headers are in the same order
        for i in range(len(taxon_labels)):
            assert def_col_headers[i] == def_row_headers[i]

        # Check the sum of the distance matrix, should be = ?
        assert default_order_matrix.data.sum() == distance_sum

        # Shuffle taxon labels and use them to order return matrix
        random.shuffle(taxon_labels)
        # Get the ordered distance matrix
        ordered_matrix = my_tree.get_distance_matrix_dendropy(
            ordered_labels=taxon_labels)
        ord_col_headers = ordered_matrix.get_column_headers()
        ord_row_headers = ordered_matrix.get_row_headers()

        # Ensure that headers are in the same order and match shuffled taxon
        #    labels
        for i in range(len(taxon_labels)):
            assert ord_col_headers[i] == ord_row_headers[i]
            assert ord_col_headers[i] == taxon_labels[i]

        # Check the sum of the distance matrix, should be = ?
        assert ordered_matrix.data.sum() == distance_sum

    # .....................................
    def test_get_distance_matrix_methods_with_attribute(self):
        """Test the get_distance_matrix versus get_distance_matrix_dendropy

        Tests that the distance matrix generated by the two methods produce
        the same results
        """
        # Set up tree
        nexus_string = """\
#NEXUS

BEGIN TAXA;
    DIMENSIONS NTAX=4;
    TAXLABELS
        Taxon_1
[&myatt=value1]
        Taxon_2
[&myatt=value2]
        Taxon_3
[&myatt=value3]
        Taxon_4
[&myatt=value4]
  ;
END;

BEGIN TREES;
    TREE 1 = ((Taxon_1:0.2,Taxon_4:0.2):0.1,(Taxon_2:0.1,Taxon_3:0.1):0.2);
END;
"""
        distance_sum = 6.0
        taxon_labels = ['value1', 'value2', 'value3', 'value4']
        my_tree = tree.TreeWrapper.get(data=nexus_string, schema='nexus')

        # Get the distance matrices
        m1_distance_matrix = my_tree.get_distance_matrix(
            label_attribute='myatt')
        m2_distance_matrix = my_tree.get_distance_matrix_dendropy(
            label_attribute='myatt')

        # Get headers for both
        m1_row_headers = m1_distance_matrix.get_row_headers()
        m1_col_headers = m1_distance_matrix.get_column_headers()
        m2_row_headers = m2_distance_matrix.get_row_headers()
        m2_col_headers = m2_distance_matrix.get_column_headers()

        # Ensure that headers are in the same order
        for i in range(len(taxon_labels)):
            assert m1_row_headers[i] == m1_col_headers[i]
            assert m2_row_headers[i] == m2_col_headers[i]
            assert m1_row_headers[i] == m2_col_headers[i]

        # Check the sum of the distance matrix, should be = 6.0
        assert m1_distance_matrix.data.sum() == distance_sum
        assert m2_distance_matrix.data.sum() == distance_sum

        # Shuffle taxon labels and use them to order return matrix
        random.shuffle(taxon_labels)
        # Get the distance matrices
        m1_distance_matrix_ord = my_tree.get_distance_matrix(
            label_attribute='myatt', ordered_labels=taxon_labels)
        m2_distance_matrix_ord = my_tree.get_distance_matrix_dendropy(
            label_attribute='myatt', ordered_labels=taxon_labels)

        # Get headers for both
        m1_row_headers_ord = m1_distance_matrix_ord.get_row_headers()
        m1_col_headers_ord = m1_distance_matrix_ord.get_column_headers()
        m2_row_headers_ord = m2_distance_matrix_ord.get_row_headers()
        m2_col_headers_ord = m2_distance_matrix_ord.get_column_headers()

        # Ensure that headers are in the same order
        for i in range(len(taxon_labels)):
            assert m1_row_headers_ord[i] == m1_col_headers_ord[i]
            assert m2_row_headers_ord[i] == m2_col_headers_ord[i]
            assert m1_row_headers_ord[i] == m2_col_headers_ord[i]
            assert m2_col_headers_ord[i] == taxon_labels[i]

        # Check the sum of the distance matrix, should be = 6.0
        assert m1_distance_matrix_ord.data.sum() == distance_sum
        assert m2_distance_matrix_ord.data.sum() == distance_sum

    # .....................................
    def test_get_distance_matrix_methods_with_label(self):
        """Test the get_distance_matrix versus get_distance_matrix_dendropy

        Tests that the distance matrix generated by the two methods produce
        the same results
        """
        # Set up tree
        nexus_string = """\
#NEXUS

BEGIN TAXA;
    DIMENSIONS NTAX=4;
    TAXLABELS
        Taxon_1
[&myatt=value1]
        Taxon_2
[&myatt=value2]
        Taxon_3
[&myatt=value3]
        Taxon_4
[&myatt=value4]
  ;
END;

BEGIN TREES;
    TREE 1 = ((Taxon_1:0.2,Taxon_4:0.2):0.1,(Taxon_2:0.1,Taxon_3:0.1):0.2);
END;
"""
        distance_sum = 6.0
        taxon_labels = ['Taxon 1', 'Taxon 2', 'Taxon 3', 'Taxon 4']
        my_tree = tree.TreeWrapper.get(data=nexus_string, schema='nexus')

        # Get the distance matrices
        m1_distance_matrix = my_tree.get_distance_matrix()
        m2_distance_matrix = my_tree.get_distance_matrix_dendropy()

        # Get headers for both
        m1_row_headers = m1_distance_matrix.get_row_headers()
        m1_col_headers = m1_distance_matrix.get_column_headers()
        m2_row_headers = m2_distance_matrix.get_row_headers()
        m2_col_headers = m2_distance_matrix.get_column_headers()

        # Ensure that headers are in the same order
        for i in range(len(taxon_labels)):
            assert m1_row_headers[i] == m1_col_headers[i]
            assert m2_row_headers[i] == m2_col_headers[i]
            assert m1_row_headers[i] == m2_col_headers[i]

        # Check the sum of the distance matrix, should be = 6.0
        assert m1_distance_matrix.data.sum() == distance_sum
        assert m2_distance_matrix.data.sum() == distance_sum

        # Shuffle taxon labels and use them to order return matrix
        random.shuffle(taxon_labels)
        # Get the distance matrices
        m1_distance_matrix_ord = my_tree.get_distance_matrix(
            ordered_labels=taxon_labels)
        m2_distance_matrix_ord = my_tree.get_distance_matrix_dendropy(
            ordered_labels=taxon_labels)

        # Get headers for both
        m1_row_headers_ord = m1_distance_matrix_ord.get_row_headers()
        m1_col_headers_ord = m1_distance_matrix_ord.get_column_headers()
        m2_row_headers_ord = m2_distance_matrix_ord.get_row_headers()
        m2_col_headers_ord = m2_distance_matrix_ord.get_column_headers()

        # Ensure that headers are in the same order
        for i in range(len(taxon_labels)):
            assert m1_row_headers_ord[i] == m1_col_headers_ord[i]
            assert m2_row_headers_ord[i] == m2_col_headers_ord[i]
            assert m1_row_headers_ord[i] == m2_col_headers_ord[i]
            assert m2_col_headers_ord[i] == taxon_labels[i]

        # Check the sum of the distance matrix, should be = 6.0
        assert m1_distance_matrix_ord.data.sum() == distance_sum
        assert m2_distance_matrix_ord.data.sum() == distance_sum

    # .....................................
    def test_get_distance_matrix_with_attribute(self):
        """Test the get_distance_matrix method using attribute labels

        Tests that the distance matrix generated by the get_distance_matrix
        method is as expected when using attribute labels for the headers
        """
        # Set up tree
        nexus_string = """\
#NEXUS

BEGIN TAXA;
    DIMENSIONS NTAX=4;
    TAXLABELS
        Taxon_1
[&myatt=value1]
        Taxon_2
[&myatt=value2]
        Taxon_3
[&myatt=value3]
        Taxon_4
[&myatt=value4]
  ;
END;

BEGIN TREES;
    TREE 1 = ((Taxon_1:0.2,Taxon_4:0.2):0.1,(Taxon_2:0.1,Taxon_3:0.1):0.2);
END;
"""
        distance_sum = 6.0
        taxon_labels = ['value1', 'value2', 'value3', 'value4']
        my_tree = tree.TreeWrapper.get(data=nexus_string, schema='nexus')

        # Get default ordered distance matrix
        default_order_matrix = my_tree.get_distance_matrix(
            label_attribute='myatt')
        def_col_headers = default_order_matrix.get_column_headers()
        def_row_headers = default_order_matrix.get_row_headers()

        # Ensure that headers are in the same order
        for i in range(len(taxon_labels)):
            assert def_col_headers[i] == def_row_headers[i]

        # Check the sum of the distance matrix, should be = ?
        assert default_order_matrix.data.sum() == distance_sum

        # Shuffle taxon labels and use them to order return matrix
        random.shuffle(taxon_labels)
        # Get the ordered distance matrix
        ordered_matrix = my_tree.get_distance_matrix(
            label_attribute='myatt', ordered_labels=taxon_labels)
        ord_col_headers = ordered_matrix.get_column_headers()
        ord_row_headers = ordered_matrix.get_row_headers()

        # Ensure that headers are in the same order and match shuffled taxon
        #    labels
        for i in range(len(taxon_labels)):
            assert ord_col_headers[i] == ord_row_headers[i]
            assert ord_col_headers[i] == taxon_labels[i]

        # Check the sum of the distance matrix, should be = ?
        assert ordered_matrix.data.sum() == distance_sum

    # .....................................
    def test_get_distance_matrix_with_label(self):
        """Test the get_distance_matrix method using taxon labels

        Tests that the distance matrix generated by the get_distance_matrix
        method is as expected when using taxon labels for the headers
        """
        # Set up tree
        nexus_string = """\
#NEXUS

BEGIN TAXA;
    DIMENSIONS NTAX=4;
    TAXLABELS
        Taxon_1
[&myatt=value1]
        Taxon_2
[&myatt=value2]
        Taxon_3
[&myatt=value3]
        Taxon_4
[&myatt=value4]
  ;
END;

BEGIN TREES;
    TREE 1 = ((Taxon_1:0.2,Taxon_4:0.2):0.1,(Taxon_2:0.1,Taxon_3:0.1):0.2);
END;
"""
        distance_sum = 6.0
        taxon_labels = ['Taxon 1', 'Taxon 2', 'Taxon 3', 'Taxon 4']
        my_tree = tree.TreeWrapper.get(data=nexus_string, schema='nexus')

        # Get default ordered distance matrix
        default_order_matrix = my_tree.get_distance_matrix()
        def_col_headers = default_order_matrix.get_column_headers()
        def_row_headers = default_order_matrix.get_row_headers()

        # Ensure that headers are in the same order
        for i in range(len(taxon_labels)):
            assert def_col_headers[i] == def_row_headers[i]

        # Check the sum of the distance matrix, should be = ?
        assert default_order_matrix.data.sum() == distance_sum

        # Shuffle taxon labels and use them to order return matrix
        random.shuffle(taxon_labels)
        # Get the ordered distance matrix
        ordered_matrix = my_tree.get_distance_matrix(
            ordered_labels=taxon_labels)
        ord_col_headers = ordered_matrix.get_column_headers()
        ord_row_headers = ordered_matrix.get_row_headers()

        # Ensure that headers are in the same order and match shuffled taxon
        #    labels
        for i in range(len(taxon_labels)):
            assert ord_col_headers[i] == ord_row_headers[i]
            assert ord_col_headers[i] == taxon_labels[i]

        # Check the sum of the distance matrix, should be = ?
        assert ordered_matrix.data.sum() == distance_sum