angular.module('DonkidikApp')
	.controller('PostsPageController', function($scope, postsService){
		// properties
		$scope.posts = [];
		$scope.types = [];

		// methods
		$scope.get_types = function(){
			postsService.get_types().then(function(res){
				$scope.types = res.data;
			});

		};
		$scope.get_posts_from_server = function(){
			postsService.get_posts_from_server().then(function(res){
				$scope.posts = res.data;
			});
		};
		
		$scope.add_post_comment = function(pid, text){
			if (text == '' || text == null){
				alert("can't comment with no text")
				return;
			}
			postsService.add_post_comment(pid, text).then(function(res){
				if (res.status=='OK'){
					$scope.get_posts_from_server();
				}
				else{
					// TODO communicate this to UI
					alert("something went wrong...");
				}
			});
		};

		$scope.remove_post = function(pid){
			postsService.remove_post(pid).then(function(res){
				if (res.status=='OK'){
					$scope.get_posts_from_server();
				}
				else{
					// TODO communicate this to UI
					if (res.error) alert(res.error);
					else alert("something went wrong...");
				}
			});
		};

		$scope.post_upvote = function(post,uid){
			postsService.post_upvote(post.post_id).then(function(res){
				if (res.status=='OK'){
					// TODO disable this button
					post.score += res.change_score;
					if (res.change_score == 1){
						var i = post.downvotes.indexOf(uid);
						if (i >-1) post.downvotes.splice(i,1);
						else post.upvotes.push(uid);
					}
					else{
						var i = post.upvotes.indexOf(uid);
						if (i >-1) post.upvotes.splice(i,1);
						else post.downvotes.push(uid);
					}
				}
				else{
					// TODO communicate this to UI
					if (res.error) alert(res.error);
					else alert("something went wrong...");
				}
			});
		};

		$scope.post_downvote = function(post,uid){
			postsService.post_downvote(post.post_id).then(function(res){
				if (res.status=='OK'){
					// TODO disable this button
					post.score += res.change_score;
					if (res.change_score == 1){
						var i = post.downvotes.indexOf(uid);
						if (i >-1) post.downvotes.splice(i,1);
						else post.upvotes.push(uid);
					}
					else{
						var i = post.upvotes.indexOf(uid);
						if (i >-1) post.upvotes.splice(i,1);
						else post.downvotes.push(uid);
					}
				}
				else{
					// TODO communicate this to UI
					if (res.error) alert(res.error);
					else alert("something went wrong...");
				}
			});
		};

		$scope.change_more = function(post){
			if (post.more){
				post.more = false;
			}else{
				post.more = true;
			}
		};
		
		// first calls
		// $scope.get_types(); TODO not sure how to resolve this
		$scope.get_posts_from_server();





	});